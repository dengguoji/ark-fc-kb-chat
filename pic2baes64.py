from PIL import Image
import base64
import mimetypes
from pathlib import Path

def image_to_base64(image_path: str, with_prefix: bool = True) -> str:
    """
    将图片文件转换为 base64 字符串

    Args:
        image_path (str): 图片的路径
        with_prefix (bool): 是否添加 'data:image/xxx;base64,' 前缀，默认为 True

    Returns:ß
        str: base64 编码后的字符串（可选带 data:image/... 前缀）
    """

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"文件不存在: {image_path}")

    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"不是有效的图片文件: {image_path}")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    if with_prefix:
        return f"data:{mime_type};base64,{encoded}"
    return encoded

if __name__ == "__main__":
    img_path = "/Users/jidengguo/project/my_project/ark_fc/example.png"
    base64_str = image_to_base64(img_path, with_prefix=True)
    print(base64_str[0:100])  # 打印前100字符预览