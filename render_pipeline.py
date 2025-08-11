import os
import re
import zipfile
import subprocess
from typing import List
from get_components_src import get_src_block
import json

BASE_DIR = "/Users/jidengguo/project/my_project"
COMPONENT_DIR = os.path.join(BASE_DIR, "components-master")
TEMPLATE_PATH = os.path.join(BASE_DIR, "ark_fc", "temple.xml")
WORK_DIR = os.path.join(BASE_DIR, "circuit_test")
OUTPUT_CDDX = os.path.join(BASE_DIR, "ark_fc", "circuit_test_output.cddx")
OUTPUT_PNG = os.path.join(BASE_DIR, "ark_fc", "rendered.png")
CLI_PATH = "/Users/jidengguo/project/circuit-diagram-cli/circuit-diagram-cli"

def write_document_xml(src_block: str, elements_block: str):
    target_dir = "/Users/jidengguo/project/my_project/ark_fc/circuit_test/circuitdiagram"
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "Document.xml")
    #print(f"[DEBUG] 目标写入路径: {target_path}")

    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()
    #print(f"[DEBUG] 是否存在模板文件: {os.path.exists(TEMPLATE_PATH)}")
    #print(f"[DEBUG] 写入路径目录存在: {os.path.exists(target_dir)}")
    #print(f"[DEBUG] 模板预览内容（前300字符）:\n{template[:300]}...")
    if not template:
        raise ValueError("模板文件为空或读取失败")
    
    template = template.replace("<definitions></definitions>", f"<definitions>\n{src_block}\n</definitions>")
    template = template.replace("<elements></elements>", f"\n{elements_block.strip()}\n")

    with open(target_path, "w") as f:
        f.write(template)
    #print(f"[DEBUG] Document.xml 写入成功")

def zip_to_cddx(folder_path: str, output_path: str):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Only include the contents of folder_path, not the top-level folder itself.
        for root, _, files in os.walk(folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, folder_path)
                zipf.write(abs_path, rel_path)

def render_cddx_to_png(cddx_path: str, output_path: str):
    cmd = [
        CLI_PATH, "circuit",
        "--components", COMPONENT_DIR,   
        "-o", output_path,
        "--grid",
        "--renderer","Skia",
        "--debug-layout",
        "--scale", "2",
        cddx_path
    ]
    subprocess.run(cmd, check=True)

def render_pipeline(elements_xml: str) -> str:
    try:
        # 从临时文件读取元件名
        with open(os.path.join(BASE_DIR, "ark_fc", "component_names.json"), "r") as f:
            names = json.load(f)
        #print(f"[DEBUG] 读取到的元件名称: {names}")
        # 获取src
        src_block = get_src_block(names)
        #print(f"[DEBUG] 获取到的 <src> 块:\n{src_block}")
        # 拼装 Document.xml
        write_document_xml(src_block, elements_xml)
        #print(f"[DEBUG] Document.xml 已生成，路径: {os.path.join(WORK_DIR, 'circuitdiagram', 'Document.xml')}")
        # 压缩为 .cddx
        zip_to_cddx("/Users/jidengguo/project/my_project/ark_fc/circuit_test", OUTPUT_CDDX)
        #print(f"[DEBUG] 压缩完成，输出文件: {OUTPUT_CDDX}")
        # 渲染为图片
        render_cddx_to_png(OUTPUT_CDDX, OUTPUT_PNG)
        #print(f"[DEBUG] 渲染完成，输出文件: {OUTPUT_PNG}")
        return OUTPUT_PNG
    except Exception as e:
        raise


if __name__ == "__main__":
    # 示例用法
    elements_xml = """
<elements>
  <c id="0" tp="41" x="100" y="200" o="h" sz="100" flp="false">
    <prs>
      <p k="t" v="Generic" />
      <p k="islit" v="false" />
    </prs>
  </c>
  <c id="1" tp="64" x="300" y="300" o="h" sz="100" flp="false">
    <prs>
      <p k="style" v="IEC" />
      <p k="text" v="" />
      <p k="resistance" v="4700" />
      <p k="showResistance" v="true" />
      <p k="t" v="Standard" />
    </prs>
  </c>
  <c id="2" tp="68" x="500" y="300" o="h" sz="100" flp="false">
    <prs>
      <p k="voltage" v="5" />
      <p k="frequency" v="50" />
      <p k="showvoltage" v="true" />
      <p k="t" v="DC" />
    </prs>
  </c>
  <w x="200" y="200" o="v" sz="100" flp="false" />
  <w x="200" y="300" o="h" sz="100" flp="false" />
  <w x="400" y="300" o="h" sz="100" flp="false" />
  <w x="600" y="300" o="v" sz="-100" flp="false" />
  <w x="600" y="200" o="h" sz="-500" flp="false" />
</elements>
    """
    output_image = render_pipeline(elements_xml)
    #print(f"渲染结果图片路径: {output_image}")