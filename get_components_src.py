import os
import xml.etree.ElementTree as ET
import glob
import json

def get_src_block(names, base_dir="/Users/jidengguo/project/my_project/components-master"):
    """
    根据元件名称列表生成 <src> 块中的 XML 内容。
    :param names: 元件名称列表，如 ["lamp", "cell"]
    :param base_dir: 组件存储的根目录路径
    :return: 字符串形式的 <src> 块内容
    """
    ns = "http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/document/component-descriptions"
    src_ns = "http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/components/common"
    lines = [f'\t\t<src col="{src_ns}">']

    all_paths = glob.glob(os.path.join(base_dir, "**", "*.xml"), recursive=True)

    with open('/Users/jidengguo/project/my_project/ccdx/component_list.json', 'r') as f:
        component_names = json.load(f)
    def normalize(s):
        return s.lower().replace(" ", "")
    name_to_id_map = {normalize(item["name"]): item["id"] for item in component_names}


    for idx, name in enumerate(names):
        component_path = None
        for p in all_paths:
            try:
                tree = ET.parse(p)
                root = tree.getroot()
                for meta in root.findall(".//{*}meta"):
                    if meta.attrib.get("name") == "name":
                        internal_name = meta.attrib.get("value", "")
                        if normalize(internal_name) == normalize(name):
                            component_path = p
                            break
                if component_path:
                    break
            except ET.ParseError:
                continue

        if not component_path:
            continue

        tree = ET.parse(component_path)
        root = tree.getroot()
        guid = ""
        version = ""
        for meta in root.findall(".//{*}meta"):
            if meta.attrib.get("name") == "guid":
                guid = meta.attrib.get("value", "")
            elif meta.attrib.get("name") == "version":
                version = meta.attrib.get("value", "")
        #print(f"[DEBUG] Extracted GUID: {guid}, Version: {version}")
        id = name_to_id_map.get(normalize(name), idx)  # 使用映射获取 ID，若未找到则使用 idx
        lines.append(f'\t\t\t<add id="{id}" item="{name}" p4:guid="{guid}"\n'
                     f'\t\t\t\tp4:version="{version}"\n'
                     f'\t\t\t\txmlns:p4="{ns}" />')

    lines.append("\t\t</src>")
    return "\n".join(lines)

if __name__ == "__main__":
    # 示例用法
    component_names = ["Integrated Circuit   4x25","555 Oscillator"]
    src_block = get_src_block(component_names) 
    print(src_block)
    # 输出示例
    # <src col="http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/components/common">
    #     <add id="0" item="lamp" p4:guid="..." p4:version="..." xmlns:p4="http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/document/component-descriptions" />
    #     <add id="1" item="cell" p4:guid="..." p4:version="..." xmlns:p4="http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/document/component-descriptions" />
    # </src>