#!/usr/bin/env python3

def fix_file(filename):
    with open(filename) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if this line starts a print statement (after stripping leading spaces)
        stripped = line.lstrip()
        if stripped.startswith('print(') and ')' not in stripped:
            # Start of a multi-line print statement
            start_index = i
            base_indent = len(line) - len(line.lstrip())
            # Find the end of the print statement
            j = i + 1
            while j < len(lines):
                if ')' in lines[j]:
                    end_index = j
                    break
                j += 1
            else:
                # Didn't find a closing parenthesis, skip
                i += 1
                continue

            # Remove any existing # noqa: T201 comments from lines[start_index:end_index+1]
            for k in range(start_index, end_index+1):
                lines[k] = lines[k].rstrip()
                # Remove trailing spaces and then check for the comment
                # We'll remove the comment if it's at the end of the line
                if lines[k].endswith('  # noqa: T201'):
                    lines[k] = lines[k][:-len('  # noqa: T201')]
                else:
                    # Try to remove the comment even if there are varying spaces
                    # We'll split by '#' and check if the last part is ' noqa: T201' (with possible leading spaces)
                    parts = lines[k].split('#')
                    if len(parts) > 1 and parts[-1].strip() == 'noqa: T201':
                        # Rejoin the parts before the comment
                        lines[k] = '#'.join(parts[:-1]).rstrip()

            # Now, modify the first line: add the comment after the opening parenthesis
            # We want to change: "    print(" to "    print(  # noqa: T201"
            # But note: the line might have more after the opening parenthesis?
            # Actually, the line is exactly the indentation plus "print(" (because we checked that there's no closing parenthesis)
            # However, there might be spaces after the opening parenthesis?
            # Let's assume the line is exactly the indentation plus "print(" (with possible trailing spaces)
            # We'll strip the line, then add the comment, then re-add the indentation.
            first_line_stripped = lines[start_index].strip()
            # It should be "print("
            if first_line_stripped == 'print(':
                lines[start_index] = ' ' * base_indent + 'print(  # noqa: T201'
            else:
                # If there is something else, we try to insert the comment after the opening parenthesis
                # Find the index of the opening parenthesis
                open_paren_index = first_line_stripped.find('(')
                if open_paren_index != -1:
                    # Insert the comment after the opening parenthesis
                    new_stripped = first_line_stripped[:open_paren_index+1] + '  # noqa: T201' + first_line_stripped[open_paren_index+1:]
                    lines[start_index] = ' ' * base_indent + new_stripped
                else:
                    # Fallback: just add the comment at the end
                    lines[start_index] = ' ' * base_indent + first_line_stripped + '  # noqa: T201'

            # Modify the last line: remove any trailing comment and just leave the closing parenthesis
            # We want to change: "        )  # noqa: T201" to "        )"
            last_line_stripped = lines[end_index].strip()
            # It should be just ")"
            if last_line_stripped == ')':
                lines[end_index] = ' ' * base_indent + ')'
            else:
                # If there is more, we try to extract just the closing parenthesis
                # Find the index of the closing parenthesis
                close_paren_index = last_line_stripped.find(')')
                if close_paren_index != -1:
                    # Take everything up to and including the closing parenthesis
                    new_stripped = last_line_stripped[:close_paren_index+1]
                    lines[end_index] = ' ' * base_indent + new_stripped
                else:
                    # Fallback: remove any comment and leave the line as is (but we already removed comments)
                    lines[end_index] = ' ' * base_indent + last_line_stripped

            # Skip the lines we have processed
            i = end_index + 1
        else:
            i += 1

    with open(filename, 'w') as f:
        f.writelines(lines)

if __name__ == '__main__':
    fix_file(r'D:\Mi unidad\Proyectos\Dorama Studio AI\apply_patch_fixed.py')
