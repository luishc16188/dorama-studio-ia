#!/usr/bin/env python3

def fix_print_statements(content):
    lines = content.splitlines()
    i = 0
    fixed_lines = []
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith('print(') and not stripped.rstrip().endswith(')'):
            # Start of a multi-line print statement
            start = i
            # Find the end line that contains the closing parenthesis
            j = i
            while j < len(lines) and ')' not in lines[j]:
                j += 1
            if j >= len(lines):
                # No closing parenthesis found, just keep as is
                fixed_lines.append(line)
                i += 1
                continue
            # Now we have from i to j (inclusive) that form the print statement
            # Collect the lines
            print_lines = lines[i:j+1]
            # Remove any existing noqa comments from these lines
            for k in range(len(print_lines)):
                # Remove trailing whitespace
                print_lines[k] = print_lines[k].rstrip()
                # If the line ends with a noqa comment, remove it
                if print_lines[k].endswith('  # noqa: T201'):
                    print_lines[k] = print_lines[k][:-len('  # noqa: T201')]
                else:
                    # Try to remove a noqa comment that might be in the middle (with spaces)
                    # We split by '#' and check if the last part is 'noqa: T201'
                    parts = print_lines[k].split('#')
                    if len(parts) > 1 and parts[-1].strip() == 'noqa: T201':
                        # Rejoin without the last part
                        print_lines[k] = '#'.join(parts[:-1]).rstrip()
            # Now combine the lines into a single line: join with a space
            combined = ' '.join([line.strip() for line in print_lines])
            # Now we need to ensure that the combined string is a valid print statement
            # We'll just use it as is.
            # Determine the base indentation of the first line
            base_indent = len(line) - len(line.lstrip())
            # Add the noqa comment at the end
            combined += '  # noqa: T201'
            fixed_lines.append(' ' * base_indent + combined)
            i = j + 1
        else:
            fixed_lines.append(line)
            i += 1
    return '\n'.join(fixed_lines) + '\n'

def main():
    filename = r'D:\Mi unidad\Proyectos\Dorama Studio AI\apply_patch_fixed.py'
    with open(filename) as f:
        content = f.read()
    fixed_content = fix_print_statements(content)
    with open(filename, 'w') as f:
        f.write(fixed_content)

if __name__ == '__main__':
    main()
