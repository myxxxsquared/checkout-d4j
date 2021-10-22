
import os
import subprocess

root_folder = "/home/wenjie/work/d-checkout"

def load_bugs():
    for line in open('all.csv'):
        line = line.strip()
        if not line:
            continue

        line = line.split('\t')
        identifier, _, _, bugs, _ = line
        if identifier == 'Identifier':
            continue

        bugs = bugs.split(',')
        bugs_list = []
        for x in bugs:
            if '-' in x:
                x, y = x.split('-')
                bugs_list.extend(range(int(x), int(y)+1))
            else:
                bugs_list.append(int(x))

        yield identifier, bugs_list

def run_d4j_export(folder, export_text):
    ret = subprocess.run(f'cd {folder}; defects4j export -p {export_text}', stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
    stdout = ret.stdout.decode('utf-8')
    print('d4j export', export_text, ret.returncode, stdout)
    return stdout
    

TXT_BEGIN = """<?xml version="1.0" encoding="UTF-8"?>
<classpath>
	<classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
"""
TXT_END = """</classpath>
"""

def main():
    for identifier, bugs_list in load_bugs():
        for bug in bugs_list:
            out_folder = os.path.join(root_folder, f"{identifier}-{bug}")
            # ret = subprocess.run(["rm", "-rf", out_folder], shell=False)
            # print('rm:', ret.returncode)
            # ret = subprocess.run(["defects4j", "checkout", "-p", identifier, "-v", f"{bug}b", "-w", out_folder], shell=False)
            # print('checkout:', ret.returncode)
            # ret = subprocess.run(["rsync", "-a", "./template/", out_folder], shell=False)
            # print('rsync:', ret.returncode)

            txt = TXT_BEGIN

            src_classes = run_d4j_export(out_folder, "dir.src.classes")
            txt += f'\t<classpathentry kind="src" path="{src_classes}"/>\n'
            src_classes = run_d4j_export(out_folder, "dir.src.tests")
            txt += f'\t<classpathentry kind="src" path="{src_classes}"/>\n'

            cps = set()
            cp = run_d4j_export(out_folder, "cp.compile")
            cps.update((x for x in cp.split(':') if x.endswith('.jar')))
            cp = run_d4j_export(out_folder, "cp.test")
            cps.update((x for x in cp.split(':') if x.endswith('.jar')))
            for cp in cps:
                txt += f'\t<classpathentry kind="lib" path="{cp}"/>\n'

            dst_classes = run_d4j_export(out_folder, "dir.bin.classes")
            txt += f'\t<classpathentry kind="output" path="{dst_classes}"/>\n'

            txt += TXT_END

            with open(f"{out_folder}/.classpath", "wt") as classpathfile:
                classpathfile.write(txt)

        #     break
        # break

if __name__ == "__main__":
    main()
