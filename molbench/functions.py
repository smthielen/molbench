from . import logger as log


def substitute_template(template: str, subvals: dict) -> str:
    while True:
        start = template.find("[[")
        stop = template.find("]]")
        if start == -1 or stop == -1:
            break
        key = template[start+2:stop]
        val = subvals.get(key, None)
        if val is None:
            log.error(f"No value for required parameter {key} "
                      f"available. Available are {subvals}.",
                      "substitute_template", KeyError)
        template = template.replace(template[start:stop+2], str(val))
    return template
