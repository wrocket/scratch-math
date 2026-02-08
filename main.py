import subprocess
import os
import sys
import tempfile


def create_markdown(tex_lines: list[str]) -> str:
    # Strip leading empty lines
    start_index = 0
    while start_index < len(tex_lines) and not tex_lines[start_index].strip():
        start_index += 1

    # Strip trailing empty lines
    end_index = len(tex_lines) - 1
    while end_index >= start_index and not tex_lines[end_index].strip():
        end_index -= 1

    # If all lines are empty or tex_lines was empty initially, return an empty list for processing
    if start_index > end_index:
        processed_tex_lines = []
    else:
        processed_tex_lines = tex_lines[start_index : end_index + 1]

    result = ["$$"]
    result.extend(processed_tex_lines)
    result.extend(["$$", "```"])
    result.extend(processed_tex_lines)
    result.append("```")
    return "\n".join(result)


def convert_markdown_to_html(markdown: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete_on_close=True) as fd:
            fd.write(markdown)
            fd.flush()
            pandoc_command = [
                "pandoc",
                "-i",
                fd.name,
                "-f",
                "gfm",
                "-t",
                "html5",
                "--mathml",
            ]
            result = subprocess.run(
                pandoc_command, capture_output=True, text=True, check=True
            )
            return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error during pandoc conversion: {e}", file=sys.stderr)
        print(f"Pandoc stderr: {e.stderr}", file=sys.stderr)
        raise


def finish_page(math_html):
    with open("base.css", "r") as fd:
        css = fd.read()
    return f'<html><head><style>{css}</style></head><body class="theme-default adaptive">{math_html}</body>'


def main():
    tex = [l.rstrip() for l in sys.stdin]
    md = create_markdown(tex)
    html_output = convert_markdown_to_html(md)
    print(finish_page(html_output))


if __name__ == "__main__":
    main()
