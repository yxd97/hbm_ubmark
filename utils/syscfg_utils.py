from typing import List,Tuple

def generate_nk_tags(ntg:int) -> List[str]:
    nk = f'nk=hbm_tg:{ntg}:'
    for i in range(ntg):
        nk += f'tg{i}'
        if i != ntg - 1:
            nk += '.'
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

def genetare_sp_tags_grp_all2all(ntg:int, nch:int, nch_per_grp:int) -> List[str]:
    if nch_per_grp not in [4, 8]:
        raise ValueError(f'Unsupported connectivity of {nch_per_grp} channels per group.')
    if nch % nch_per_grp != 0:
        raise ValueError(f'The number of channels must be a multiple of {nch_per_grp} (num of channels per groups) for group connectivity.')
    ngroups = nch // nch_per_grp
    if ntg % ngroups != 0:
        raise ValueError(f'The number of TGs must be a multiple of {ngroups} (num of groups) for group connectivity.')
    ntgs_per_grp = ntg // ngroups
    sp = []
    for i in range(ntg):
        grp_id = i // ntgs_per_grp
        ch_lo = grp_id * nch_per_grp
        ch_hi = ch_lo + nch_per_grp - 1
        sp.append(f'sp=tg{i}.maxi:HBM[{ch_lo}:{ch_hi}]\n')
    return sp

def generate_sp_tags(ntg:int, nch:int, connectivity:str) -> List[str]:
    if connectivity.startswith('grp'):
        nch_per_grp = int(connectivity.split('_')[0].strip('grp'))
        return genetare_sp_tags_grp_all2all(ntg, nch, nch_per_grp)


    elif connectivity == 'all2all':
        return generate_sp_tags_all2all(ntg, nch)
    elif connectivity == 'one2one':
        return generate_sp_tags_one2one(ntg, nch)
    elif connectivity == 'one2all':
        return generate_sp_tags_one2all(nch)
    else:
        raise ValueError(f'Unsupported connectivity {connectivity}')
