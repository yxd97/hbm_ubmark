from typing import List,Tuple

def generate_nk_tags(ntg:int) -> List[str]:
    nk = f'nk=hbm_tg:{ntg}'
    for i in range(ntg):
        nk += f'.tg{i}'
    nk += '\n'
    return [nk]

def generate_slr_tags(ntg_slrs:Tuple[int, int, int]) -> List[str]:
    slr = []
    ntg_slr0, ntg_slr1, ntg_slr2 = ntg_slrs
    tgid = 0
    for _ in range(ntg_slr0):
        slr.append(f'slr=tg{tgid}:SLR0\n')
        tgid += 1
    for _ in range(ntg_slr1):
        slr.append(f'slr=tg{tgid}:SLR1\n')
        tgid += 1
    for _ in range(ntg_slr2):
        slr.append(f'slr=tg{tgid}:SLR2\n')
        tgid += 1
    return slr

def generate_sp_tags_all2all(ntg:int, nch:int) -> List[str]:
    sp = []
    for i in range(ntg):
        sp.append(f'sp=tg{i}.maxi:HBM[0:{nch-1}]\n')
    return sp

def generate_sp_tags_one2one(ntg:int, nch:int) -> List[str]:
    if ntg != nch:
        raise ValueError('The number of TGs and channels must be the same for one-to-one connectivity.')
    sp = []
    for i in range(ntg):
        sp.append(f'sp=tg{i}.maxi:HBM[{i}]\n')
    return sp

def generate_sp_tags_one2all(nch:int) -> List[str]:
    sp = []
    sp.append(f'sp=tg0.maxi:HBM[0:{nch-1}]\n')
    return sp

def genetare_sp_tags_grp_all2all(ntg:int, nch:int, group_size:int) -> List[str]:
    #TODO: implement this
    sp = ['# Grouped connectivitiy not supported yet.\n']
    return sp

def generate_sp_tags(ntg:int, nch:int, connectivity:str) -> List[str]:
    if connectivity.startswith('grp'):
        group_size = int(connectivity[3])
        if group_size in [4, 8]:
            return genetare_sp_tags_grp_all2all(ntg, nch, group_size)
        else:
            raise ValueError(f'Unsupported group size {group_size}')
    else:
        if ntg == nch:
            return generate_sp_tags_one2one(ntg, nch)
        elif ntg == 1:
            return generate_sp_tags_one2all(nch)
        else:
            return generate_sp_tags_all2all(ntg, nch)
