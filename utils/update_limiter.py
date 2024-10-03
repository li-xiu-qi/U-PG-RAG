def update_limit(dicts: list, rpm_factor: float, tpm_factor: float):
    for d in dicts:
        d['rpm'] *= rpm_factor
        d['tpm'] *= tpm_factor
    return dicts