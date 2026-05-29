def export_sample(sample: dict, site_id: str = 'gary') -> dict:
    return {'site_id': site_id, 'telemetry': sample}
