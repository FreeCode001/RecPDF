"""
RecPDF包:
一个用于解析PDF文档内容的Python包，可识别PDF中的文本、图片、表格、公式等元素。
主接口：parse_pdf
    @param pdf_path: PDF文件路径
    @param output_dir: 输出目录
    @param settings: 配置参数
    @param workers: 工作线程数
    @param prompt: 解析提示词
    @param rect_prompt: 矩形解析提示词
    @param sys_prompt: 系统提示词
    @return: 解析后的markdown内容, 矩形图片路径列表
工作流程：
    1. 读取PDF文件
    2. 提取PDF页面中的图片区域和文本区域
    3. 合并和吸附图片和文本区域
    4. 页面矩形区域标注，保存页面图片和矩形区域图片
    5. 创建页面解析线程池
    6. 调用大模型解析页面图片
    7. 保存解析结果到Markdown文件
"""
import logging
import fitz
import os
import base64
import shapely.geometry as sg
from typing import List, Tuple
from shapely.validation import explain_validity
from .utils import merge_rects, adsorb_rects_to_rects, remove_markdown_backticks
from .prompts import DEFAULT_PARSER_PROMPT, DEFAULT_RECT_PROMPT, DEFAULT_SYS_PROMPT, REFINE_PROMPT, REFINE_SYS_PROMPT
from .models import init_parser_model, init_refine_model
from .config import Settings
import concurrent.futures


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_rects(page: fitz.Page):
    """
    解析页面中的绘图，并合并相邻的矩形。
    @param page: 页面
    @return: 矩形列表
    """

    # 1.提取PDF页面中的矢量图形，并转换为shapely的矩形列表
    drawings = page.get_drawings()
    ## 忽略掉长度小于30的水平直线
    is_short_line = lambda x: abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < 30
    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]
    rect_list = [sg.box(*drawing['rect']) for drawing in drawings]

    # 2.提取PDF页面中的图像区域，并转换为shapely的矩形列表
    images = page.get_image_info()
    image_rects = [sg.box(*image['bbox']) for image in images]
    
    # 3.合并矢量图形和图像区域的矩形列表
    rect_list += image_rects
    merged_rects = merge_rects(rect_list, distance=10, horizontal_distance=100)
    merged_rects = [rect for rect in merged_rects if explain_validity(rect) == 'Valid Geometry']

    # 4.提取PDF页面中的文本区域，并转换为shapely的矩形列表，区分大文本块和小文本块
    is_large_content = lambda x: (len(x[4]) / max(1, len(x[4].split('\n')))) > 5
    small_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if not is_large_content(x)]
    large_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if is_large_content(x)]
    
    # 5.将大文本块和小文本块分别处理，将靠近的文本块吸附到图形图像矩形列表中
    _, merged_rects = adsorb_rects_to_rects(large_text_area_rects, merged_rects, distance=0.1) # 完全相交
    _, merged_rects = adsorb_rects_to_rects(small_text_area_rects, merged_rects, distance=5) # 靠近

    # 6.再做一次矩形列表合并
    merged_rects = merge_rects(merged_rects, distance=10)

    # 7.过滤比较小的矩形
    merged_rects = [rect for rect in merged_rects if rect.bounds[2] - rect.bounds[0] > 20 and rect.bounds[3] - rect.bounds[1] > 20]
    
    # 8.返回最终的矩形边界列表
    return [rect.bounds for rect in merged_rects]


def parse_pdf_to_images(pdf_path, output_dir = './'):
    """
    解析PDF文件到图片，并保存到输出目录。
    @param pdf_path: PDF文件路径
    @param output_dir: 输出目录
    @return image_infos: 图片信息列表(图片路径, 矩形图片路径列表)
    """
    
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    image_infos = []

    # 1.遍历PDF文件中的每一页
    for page_index, page in enumerate(pdf_document):
        logger.info(f'parse page: {page_index}')
        rect_images = []

        # 2.解析页面中的矩形区域
        rects = parse_rects(page)

        # 3.遍历每个矩形区域
        for index, rect in enumerate(rects):
            fitz_rect = fitz.Rect(rect)

            # 4.获取矩形区域的像素映射数据，并保存为图片
            pix = page.get_pixmap(clip=fitz_rect, matrix=fitz.Matrix(4, 4))
            name = f'{page_index}_{index}.png'
            pix.save(os.path.join(output_dir, name))
            rect_images.append(name)

            # 5.在页面上绘制红色矩形边框
            big_fitz_rect = fitz.Rect(fitz_rect.x0 - 1, fitz_rect.y0 - 1, fitz_rect.x1 + 1, fitz_rect.y1 + 1)
            page.draw_rect(big_fitz_rect, color=(1, 0, 0), width=1)  # 空心矩形

            # 画矩形区域(实心)
            # page.draw_rect(big_fitz_rect, color=(1, 0, 0), fill=(1, 0, 0))

            # 6.在矩形内的左上角写上矩形的索引name，添加一些偏移量
            text_x = fitz_rect.x0 + 2
            text_y = fitz_rect.y0 + 10
            text_rect = fitz.Rect(text_x, text_y - 9, text_x + 80, text_y + 2)
            page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1))  # 绘制白色背景矩形
            page.insert_text((text_x, text_y), name, fontsize=10, color=(1, 0, 0))  # 插入文字
        # 7.获取页面高清像素映射数据，并保存为图片。（页面上已标注它所有的矩形区域和索引文字）
        page_image_with_rects = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        page_image = os.path.join(output_dir, f'{page_index}.png')
        page_image_with_rects.save(page_image)
        # 8.保存图片信息列表：列表元素为(页面图片文件路径, 矩形图片路径列表)
        image_infos.append((page_image, rect_images))

    pdf_document.close()
    return image_infos


# 解析PDF文件到markdown文件
def parse_pdf(
        pdf_path: str,
        output_dir: str = './',
        settings: Settings = None,
        workers: int = 1,
        prompt = DEFAULT_PARSER_PROMPT,
        rect_prompt = DEFAULT_RECT_PROMPT,
        sys_prompt = DEFAULT_SYS_PROMPT,
) -> Tuple[str, List[str]]:
    """
    解析PDF文件到markdown文件。
    @param pdf_path: PDF文件路径
    @param output_dir: 输出目录
    @return: 解析后的markdown内容, 矩形图片路径列表
    """
    if not settings:
        settings = Settings()

    api_key = settings.parser_api_key
    base_url = settings.parser_api_base
    model = settings.parser_api_model
    
    file_name_as_subpath = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = os.path.join(output_dir, file_name_as_subpath)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.basename(pdf_path).replace('.pdf', '.md')
    image_infos = parse_pdf_to_images(pdf_path, output_dir=output_dir)

    # 初始化解析模型
    if not api_key or not base_url or not model:
        raise ValueError("api_key, base_url, and model are required parameters. Config in .env file or pass as arguments.")
    parse_model = init_parser_model(api_key, base_url, model)

    # Process images with Vision Large Model
    def _process_page(index: int, image_info: Tuple[str, List[str]]) -> Tuple[int, str]:
        page_image, rect_images = image_info
        local_prompt = prompt
        if rect_images:
            local_prompt += rect_prompt + ', '.join(rect_images)
        
        # 打开页面图片文件
        with open(page_image, "rb") as image_file:
            # 调用大模型解析页面图片
            try:
                messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": local_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"}}
                        ]}
                    ]
                logger.info(f' extract page: {index+1}')
                response = parse_model.invoke(messages)

                # 检查 response.content 是否为空字符串
                #if response.content:
                #    print(response)
                #    return index, f"Error: Empty content in API response for page {index+1}"
                    
                content = response.content
                return index, content
            except Exception as e:
                # 捕获所有异常并返回错误信息
                return index, f"Error processing page {index+1}: {str(e)}"

    contents = [None] * len(image_infos)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_process_page, index, image_info) for index, image_info in enumerate(image_infos)]
        for future in concurrent.futures.as_completed(futures):
            index, content = future.result()
            content = remove_markdown_backticks(content)
            contents[index] = content

    # 保存解析后的markdown文件
    output_path = os.path.join(output_dir, file_name)
    content = '\n\n'.join(contents)
    logger.info(f' save output file: {output_path}')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    #  删除中间过程的图片
    all_rect_images = []
    for page_image, rect_images in image_infos:
        if os.path.exists(page_image):
            os.remove(page_image)
        all_rect_images.extend(rect_images)

    return content, all_rect_images

# 格式优化markdown文件
def refine_markdown(
        markdown_path: str,
        settings: Settings = None,
        prompt = REFINE_PROMPT,
        sys_prompt = REFINE_SYS_PROMPT,
) -> str:
    """
    调整markdown内容结构。
    @param markdown: 输入的markdown内容
    @return: 调整后的markdown内容
    """
    if not settings:
        settings = Settings()
    
    api_key = settings.refine_api_key
    base_url = settings.refine_api_base
    model = settings.refine_api_model
    
    # 初始化大模型
    if not api_key or not base_url or not model:
        raise ValueError("api_key, base_url, and model are required parameters.")
    refine_model = init_refine_model(api_key, base_url, model)

    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown = f.read()
    prompt = prompt.format(markdown=markdown)
    messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
        ]}
    ]
    logger.info(f' start refine markdown: {markdown_path}')
    response = refine_model.invoke(messages)

    output_file = markdown_path.replace('.md', '_refined.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response.content)
    logger.info(f' save refined output file: {output_file}')
    return response.content
