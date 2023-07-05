import json

from django import template
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from markdown import markdown

register = template.Library()


@register.filter
def include_markdown(template_name):
    """
    Include a template written in markdown (rendered as HTML).
    """
    template = get_template(template_name)
    if template is None:
        raise TemplateDoesNotExist(template_name)
    markdown_text = template.render()
    html_text = markdown(
        markdown_text, extensions=["fenced_code", "attr_list", "tables"]
    )
    return html_text


@register.filter
def pretty_json(value):
    """
    Pretty-print JSON.
    """
    return json.dumps(value, indent=4, sort_keys=True)


@register.filter
def split(value: str, sep: str = "\n"):
    """
    Split a string by a separator.
    """
    return value.split(sep)


@register.filter
def codehilite_height(value: str) -> str:
    """
    Calculate the height of a codehilite block as a CSS pixel value.
    """
    return str(int(len(value.split("\n")) * 22.39)) + "px"
