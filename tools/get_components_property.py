# get_components_property.py
import os
import xml.etree.ElementTree as ET
import re
import json

def get_components_property(names):
    """
    接收模型传入的 names 列表，查找对应元件的所有 <property> 节点内容，并为每个元件分配一个唯一 tp ID
    """
    if isinstance(names, str):
        try:
            names = json.loads(names)
        except json.JSONDecodeError:
            return f"无法解析传入的名称参数: {names}"
    elif not isinstance(names, list):
        return f"错误参数类型: {type(names)}，应为 list 或 JSON 字符串"
    base_dir = "/Users/jidengguo/project/my_project/components-master"
    ns = {'cd': 'http://schemas.circuit-diagram.org/circuitDiagramDocument/2012/component/xml'}
    result = []
    tp_counter = 0
    with open('/Users/jidengguo/project/my_project/ccdx/component_list.json', 'r') as f:
        component_names = json.load(f)
    def normalize(s):
        return s.lower().replace(" ", "")
    name_to_id_map = {normalize(item["name"]): item["id"] for item in component_names}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".xml"):
                full_path = os.path.join(root, file)
                try:
                    tree = ET.parse(full_path)
                    component = tree.getroot()
                    declaration = component.find('cd:declaration', ns)
                    if declaration is not None:
                        metas = declaration.findall('cd:meta', ns)
                        comp_name = None
                        minsize = None
                        for meta in metas:
                            meta_name = meta.attrib.get('name', '').lower()
                            if meta_name == 'name':
                                comp_name = meta.attrib.get('value', '').strip()
                            elif meta_name == 'minsize':
                                minsize = meta.attrib.get('value', '').strip()
                        if comp_name and any(name.lower() == comp_name.lower() for name in names):
                            props = declaration.findall('cd:property', ns)
                            prop_strs = []
                            for p in props:
                                for elem in p.iter():
                                    if '}' in elem.tag:
                                        elem.tag = elem.tag.split('}', 1)[1]
                                xml_str = ET.tostring(p, encoding='unicode')
                                xml_str = re.sub(r'\s+xmlns="[^"]+"', '', xml_str)
                                prop_strs.append(xml_str)

                            id = name_to_id_map.get(normalize(comp_name), tp_counter)  # 使用映射获取 ID，若未找到则使用 tp_counter
                            result.append({
                                "name": comp_name,
                                "tp": id,
                                "minsize": minsize,
                                "properties": prop_strs
                            })
                            # tp_counter += 1
                except ET.ParseError:
                    continue
    temp_path = "/Users/jidengguo/project/my_project/ark_fc/component_names.json"
    with open(temp_path, "w") as f:
        json.dump(names, f)
    # 构造字符串返回
    output_lines = []
    for item in result:
        output_lines.append(f'元件：{item["name"]} (tp={item["tp"]})')
        output_lines.append(f'固定尺寸（sz）：{item.get("minsize", "N/A")}')
        output_lines.extend(item["properties"])
        output_lines.append("")  # 添加空行
    return "\n".join(output_lines)

if __name__ == "__main__":
    model_args = {"names": ["AC-DC Converter", "Lamp"]}
    props_dict = get_components_property(model_args["names"])
    print(props_dict)
    """
    for item in props_dict:
        print(f"\n元件：{item['name']} (tp={item['tp']})")
        for p in item["properties"]:
            print(p)
            """