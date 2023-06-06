import os
import sys

dirs = []
for dir in os.listdir('.'):
    if os.path.isdir(dir) and dir not in ['utils', 'hbm_tg', 'include', 'hbm_ip_only' ,'.git']:
        dirs.append(dir)

for dir in dirs:
    os.system(f'mv {dir}/output {dir}/build')
    os.system(f'rm -rf {dir}/output/*')
    os.makedirs(f'{dir}/output/link/report', exist_ok=True)
    os.system(f'cp -r {dir}/build/output/link/report {dir}/output/link')
    os.system(f'cp -r {dir}/build/output/hbm_tg {dir}/output/hls')