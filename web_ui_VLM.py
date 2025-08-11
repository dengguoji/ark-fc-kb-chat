import gradio as gr
import ark_client
from tool_executor import execute_function_call
from judge_kb import judge_need_kb
from query_kb import query_kb
from prompts import (
    TIME_PREFIX,
    MAIN_SYSTEM_PROMPT,
    MARKDOWN_PROMPT,
    RULE_KB_PROMPT,
    RECALL_KB_PROMPT_START,
    RECALL_KB_PROMPT_END,
    CDDX_SYSTEM,   
)
import json
import datetime
import pic2baes64
# 实际返回时间
def get_time_prefix():
    return f"当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def format_messages(messages):
    try:
        return json.dumps(messages, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to format messages: {e}"

# initial system messages
"""
SYSTEM_MESSAGES = [
    {
        "role": "system",
        "content": f"It is {get_time_prefix()} now\n{MAIN_SYSTEM_PROMPT}\n{MARKDOWN_PROMPT}\n{RULE_KB_PROMPT}",
    }
]
"""
# cddx
SYSTEM_MESSAGES = [
    {
        "role": "system",
        "content": f"It is {get_time_prefix()} now\n{CDDX_SYSTEM}",
    }
]


def chat_fn(user_message, enable_kb, enable_rewrite, enable_reasoning, enable_tools, uploaded_images, messages):
    """
    Gradio streaming function. Yields updates to:
      chat_history, kb_display, reasoning_display,
      tool_call_display, tool_result_display, messages (state), messages_box, uploaded_image (cleared)
    """
    # copy states
    messages = messages.copy()
    insert_index = len(messages)
    # keep the pure user input for display/cleanup
    pure_user_input = user_message
    # determine enhanced prompt
    user_input_content = user_message
    kb_id = "0"
    kb_recalls = {}
    kb_content = ""
    kb_display = ""
    kb_messages = []
    kb_markdown = ""

    def strip_images_from_messages(msgs):
        def strip_content(content):
            if isinstance(content, list):
                return "\n".join(
                    item["text"] for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            return content

        return [
            {
                "role": m["role"],
                "content": strip_content(m["content"])
            }
            for m in msgs if m["role"] in ("system", "user", "assistant")
        ]

    if uploaded_images:
        enable_kb = False  # 图像优先
        kb_display = "⚠️ 已上传图像，本轮已自动关闭知识库"
        img_blocks = []
        for img_path in uploaded_images:
            image_url = pic2baes64.image_to_base64(img_path, with_prefix=True)
            img_blocks.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high"
                }
            })
        img_blocks.append({
            "type": "text",
            "text": pure_user_input 
        })
        pure_user_input = img_blocks
        user_input_content = pure_user_input

    if enable_kb:
        clean_messages = strip_images_from_messages(messages)
        temp_msgs = clean_messages + [{"role": "user", "content": pure_user_input}]
        kb_result_str = judge_need_kb(temp_msgs)
        try:
            kb_result = json.loads(kb_result_str)
        except Exception as e:
            kb_result = {"matches":[{"knowledge_id":"0", "rewritten_queries":[]}]}  # fallback to empty
        matches = kb_result.get("matches", [])
        if matches and matches[0].get("knowledge_id") != "0":
            sectioned_contents = []
            sectioned_struct = []
            section_num = 1
            for match in matches:
                kb_id = match.get("knowledge_id", "0")
                if enable_rewrite and match.get("rewritten_queries"):
                    queries = match.get("rewritten_queries", [])
                else:
                    queries = [pure_user_input]             
                if queries:
                    for query in queries:
                        kb_recall = query_kb(kb_id, query)  # 返回 [{'content': ..., 'score': ...}, ...]
                        if kb_recall:
                            for item in kb_recall:
                                content = item.get("content", "") if isinstance(item, dict) else str(item)
                                if content.strip():
                                    sectioned_struct.append({
                                        "section_no": section_num,
                                        "kb_id": kb_id,
                                        "query": query,
                                        "content": content 
                                    })
                                    sectioned_contents.append(
                                        f"Section {section_num} start:\n{content}\nSection {section_num} ends."
                                    )
                                    section_num += 1
            if sectioned_contents:
                kb_content = "\n".join(sectioned_contents)
            else:
                kb_content = ""

            #kb_messages = []
            if sectioned_struct:
                # 分组组装 markdown
                kb_grouped = {}
                for s in sectioned_struct:
                    kb_id = s["kb_id"]
                    query = s.get("query", "")
                    content = s["content"]
                    kb_grouped.setdefault(kb_id, {}).setdefault(query, []).append(content)

                kb_md_list = []
                for kb_id, query_dict in kb_grouped.items():
                    query_md_list = []
                    for query, section_list in query_dict.items():
                        sections_md = "\n".join([f"<blockquote>{c}</blockquote>" for c in section_list])
                        query_md = f'<details><summary>检索词：{query}</summary>\n{sections_md}\n</details>'
                        query_md_list.append(query_md)
                    kb_md = f'<details><summary>KB:{kb_id}</summary>\n' + "\n".join(query_md_list) + '\n</details>'
                    kb_md_list.append(kb_md)
                kb_markdown = "\n\n".join(kb_md_list) if kb_md_list else ""
            else:
                kb_markdown = ""
        else:
            kb_markdown = ""

        if kb_content:
            user_input_content = (
                f"{RECALL_KB_PROMPT_START}\n{kb_content}\n"
                f"{RECALL_KB_PROMPT_END}\n{pure_user_input}"
            )


    messages.insert(insert_index, {
        "role": "user",
        "content": user_input_content,
        "display": pure_user_input
    })

    def get_chat_display():
        display = []
        for m in messages:
            if m["role"] not in ("user", "assistant"):
                continue
            content = m.get("display", m["content"])

            # 若是图文结构（列表），则只保留文字部分
            if isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        texts.append(item["text"])
                    elif isinstance(item, str):
                        texts.append(item)
                display.append({"role": m["role"], "content": "\n".join(texts)})
            else:
                # 普通字符串内容直接显示
                display.append({"role": m["role"], "content": content})
        return display

    # prepare accumulators
    assistant_content = ""
    reasoning_content = ""
    current_tool_calls = {}
    tool_call_display = ""
    tool_result_display = ""

    chat_display = get_chat_display()

    # show user message immediately
    yield (
        chat_display.copy(),
        kb_markdown,
        reasoning_content,
        tool_call_display,
        tool_result_display,
        messages,
        format_messages(messages),
        None
    )

    # define the streaming generator
    def _stream():
        nonlocal assistant_content, reasoning_content
        nonlocal current_tool_calls, tool_call_display, tool_result_display
        nonlocal chat_display

        has_appended_bubble = False
        bubble_index = None

        assistant_content += ""

        # stream-chat as in conversation.py
        if enable_reasoning:
            stream = ark_client.stream_chat_reasoning(messages, enable_tools)
        else:
            stream = ark_client.stream_chat(messages, enable_tools)
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # 3) reasoning_content (stream)
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if reasoning_content == "":
                    # first time header
                    reasoning_content  # already empty
                reasoning_content += delta.reasoning_content
                yield (
                    chat_display.copy(),
                    kb_markdown,
                    reasoning_content,
                    tool_call_display,
                    tool_result_display,
                    messages,
                    format_messages(messages),
                    None
                )

            # 4) content (stream)
            if getattr(delta, "content", None):
                # for the first content in this invocation, create a new bubble
                if not has_appended_bubble:
                    chat_display.append({"role": "assistant", "content": ""})
                    bubble_index = len(chat_display) - 1
                    has_appended_bubble = True
                # append streaming text
                chat_display[bubble_index]["content"] += delta.content
                assistant_content += delta.content
                yield (
                    chat_display.copy(),
                    kb_markdown,
                    reasoning_content,
                    tool_call_display,
                    tool_result_display,
                    messages,
                    format_messages(messages),
                    None
                )

            # 5) collect tool_calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in current_tool_calls:
                        current_tool_calls[idx] = {
                            "function": {"name": tc.function.name, "arguments": ""},
                            "type": tc.type,
                            "id": tc.id,
                        }
                    current_tool_calls[idx]["function"]["arguments"] += (
                        tc.function.arguments or ""
                    )

        # after streaming, if any tool_calls exist → execute them
        if current_tool_calls:
            # 确保作用域
            assistant_content += ""
            # append assistant-final with tool_calls list
            calls_list = []
            for call in current_tool_calls.values():
                calls_list.append({
                    "id": call["id"],
                    "type": call["type"],
                    "function": {
                        "name": call["function"]["name"],
                        "arguments": call["function"]["arguments"],
                    },
                })
            messages.append({
                "role": "assistant",
                "content": assistant_content.strip(),
                "tool_calls": calls_list,
            })

            for call in current_tool_calls.values():
                # print one tool_call entry
                tc_text = (
                    f"Function: {call['function']['name']}\n"
                    f"Args: {call['function']['arguments']}"
                )
                tool_call_display += tc_text + "\n\n"
                yield (
                    chat_display.copy(),
                    kb_markdown,
                    reasoning_content,
                    tool_call_display,
                    tool_result_display,
                    messages,
                    format_messages(messages),
                    None
                )
                # execute
                try:
                    res = execute_function_call(call)
                except Exception as e:
                    res = f"工具执行异常: {e}"
                tool_result_display += res + "\n\n"
                yield (
                    chat_display.copy(),
                    kb_markdown,
                    reasoning_content,
                    tool_call_display,
                    tool_result_display,
                    messages,
                    format_messages(messages),
                    None
                )
                # record tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": res,
                })

            current_tool_calls.clear()
            # separate previous assistant result from next stream
            assistant_content = ""
            # 不插入空 assistant 消息以强制新气泡
            # 不清空 reasoning_content
            # emit a separation so UI knows to start a new bubble
            yield (
                chat_display.copy(),
                kb_markdown,
                reasoning_content,
                tool_call_display,
                tool_result_display,
                messages,
                format_messages(messages),
                None
            )
            # recursive: continue processing any further assistant output
            yield from _stream()
        else:
            assistant_content += ""
            messages.append({
                "role": "assistant",
                "content": assistant_content.strip(),
            })
            yield (
                chat_display.copy(),
                kb_markdown,
                reasoning_content,
                tool_call_display,
                tool_result_display,
                messages,
                format_messages(messages),
                None
            )

    # run the generator
    yield from _stream()

    # cleanup enhanced prompt: replace with pure input
    messages.pop(insert_index)
    messages.insert(insert_index, {
        "role": "user",
        "content": pure_user_input,
        "display": pure_user_input
    })


# Build Gradio UI
with gr.Blocks(css="""
#kb_markdown_box {
    flex: 1;
    overflow: auto;
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    box-shadow: 0 1px 4px 0 #0001;
    padding: 16px 12px;
    box-sizing: border-box;
    margin-bottom: 16px;
    margin-top: 0;
}
#tool_panel {
    height: 800px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
#tool_panel .gr-textbox {
    flex: 1;
    min-height: 0;
}
""") as demo:
    gr.Markdown("## Ark Chat UI")

    with gr.Column():
        with gr.Row():
            # 左侧列：聊天历史
            with gr.Column(scale=2):
                chat_history = gr.Chatbot(label="对话历史", height=800, type="messages")
            # 中间列：Reasoning
            with gr.Column(scale=1):
                reasoning_box = gr.Textbox(label="Reasoning Content", interactive=False, lines=37, elem_classes=["gr-textbox"])
            # 右侧列：工具区
            with gr.Column(scale=2):
                with gr.Column(elem_id="tool_panel", scale=1):
                    gr.Markdown("### Recalled KB")
                    kb_box = gr.Markdown(label="Recalled KB", elem_id="kb_markdown_box", elem_classes=["gr-textbox"])
                    tool_call_box = gr.Textbox(label="Tool Calls", interactive=False, elem_classes=["gr-textbox"])
                    tool_result_box = gr.Textbox(label="Tool Results", interactive=False, elem_classes=["gr-textbox"])

        # 下方输入区和选项
        with gr.Column(scale=1):
            uploaded_images = gr.File(file_types=[
                # 常见格式（小写+大写）
                ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif",
                ".ico", ".dib", ".icns", ".sgi", ".j2c", ".j2k", ".jp2", ".jpc", ".jpf", ".jpx",
                ".heic", ".heif",
                ".PNG", ".JPG", ".JPEG", ".GIF", ".WEBP", ".BMP", ".TIFF", ".TIF",
                ".ICO", ".DIB", ".ICNS", ".SGI", ".J2C", ".J2K", ".JP2", ".JPC", ".JPF", ".JPX",
                ".HEIC", ".HEIF"
            ],
            file_count="multiple", label="上传图片", interactive=True, height=120)
            user_input = gr.Textbox(placeholder="Type your message and hit enter", show_label=False)
        # 新增一键渲染按钮及输入输出
        with gr.Row():
            with gr.Column():
                elements_input = gr.Textbox(label="Elements XML", lines=10)
                render_button = gr.Button("一键渲染")            
            render_output = gr.Image(label="渲染图像预览")
        with gr.Row():
            kb_toggle = gr.Checkbox(label="知识库", value=False)
            rewrite_toggle = gr.Checkbox(label="改写查询", value=False)
            reasoning_toggle = gr.Checkbox(label="深度思考", value=False)
            tools_toggle = gr.Checkbox(label="工具调用", value=True)
        clear_button = gr.Button("清空历史")
        messages_box = gr.Code(label="Messages State", language="json", lines=30, interactive=False)

    # hidden states
    messages_state = gr.State(SYSTEM_MESSAGES)

    # wire up streaming
    user_input.submit(
        chat_fn,
        inputs=[user_input, kb_toggle, rewrite_toggle, reasoning_toggle, tools_toggle, uploaded_images, messages_state],
        outputs=[
            chat_history,
            kb_box,
            reasoning_box,
            tool_call_box,
            tool_result_box,
            messages_state,
            messages_box,
            uploaded_images
        ],
    )

    def clear_history():
        """
        new_system_messages = [
            {
                "role": "system",
                "content": f"It is {get_time_prefix()} now\n{MAIN_SYSTEM_PROMPT}\n{MARKDOWN_PROMPT}\n{RULE_KB_PROMPT}",
            }
        ]
        """
        # cddx
        new_system_messages = [
             {
                 "role": "system",
                 "content": f"It is {get_time_prefix()} now\n{CDDX_SYSTEM}",
             }
        ] 
        return (
            [],  # chat_history
            "",  # kb_box
            "",  # reasoning_box
            "",  # tool_call_box
            "",  # tool_result_box
            new_system_messages,  # messages_state
            format_messages(new_system_messages),  # messages_box
            None
        )

    clear_button.click(
        clear_history,
        inputs=[],
        outputs=[
            chat_history,
            kb_box,
            reasoning_box,
            tool_call_box,
            tool_result_box,
            messages_state,
            messages_box,
            uploaded_images
        ],
    )

    # 新增一键渲染功能
    def on_click_render(elements_xml):
        from render_pipeline import render_pipeline
        return render_pipeline(elements_xml)

    render_button.click(
        on_click_render,
        inputs=[elements_input],
        outputs=[render_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)