import typer
from semver import Version
from typing import Annotated, Optional
from blitz.core import BlitzCore
from rich import print
from blitz.models import BlitzResource
from rich.style import Style
from rich.panel import Panel


class SwaggerPrinter:
    POST_STYLE = Style(color="#49cc90")
    GET_STYLE = Style(color="#61affe")
    DELETE_STYLE = Style(color="#f93e3e")
    PATCH_STYLE = Style(color="#fca130")
    BOLD_STYLE = "[white bold]"

    def __init__(self, routes: list[BlitzResource]) -> None:
        self.routes = routes

    def _get_create_panel(self, resource_name: str) -> Panel:
        return Panel(
            f"[{self.POST_STYLE}]POST    [white bold]/{resource_name} [white dim frame]Create One",
            border_style=self.POST_STYLE,
        )

    def _get_read_panel(self, resource_name: str) -> list[Panel]:
        return [
            Panel(
                f"[{self.GET_STYLE}]GET     [white bold]/{resource_name} [white dim frame]Get One",
                border_style=self.GET_STYLE,
            ),
            Panel(
                f"[{self.GET_STYLE}]GET     [white bold]/{resource_name}/{{item_id}} [white dim frame]Get All",
                border_style=self.GET_STYLE,
            ),
        ]

    def _get_can_delete_panel(self, resource_name: str) -> Panel:
        return Panel(
            f"[{self.DELETE_STYLE}]DELETE  [white bold]/{resource_name}/{{item_id}} [white dim frame]Delete One",
            border_style=self.DELETE_STYLE,
        )

    def _get_can_update_panel(self, resource_name: str) -> Panel:
        return Panel(
            f"[{self.PATCH_STYLE}]PUT     [white bold]/{resource_name}/{{item_id}} [white dim frame]Update One",
            border_style=self.PATCH_STYLE,
        )

    def _get_name_panel(self, resource_name: str) -> Panel:
        return Panel(f"[white bold]{resource_name.upper()}")

    def get_panels(self) -> list[Panel | str]:
        panels: list[Panel | str] = []
        for resource in self.routes:
            resource_name = resource.config.name.lower()
            panels.append(self._get_name_panel(resource_name))
            if resource.config.can_create:
                panels.append(self._get_create_panel(resource_name))
            if resource.config.can_read:
                panels.extend(self._get_read_panel(resource_name))
            if resource.config.can_delete:
                panels.append(self._get_can_delete_panel(resource_name))
            panels.append("\n")
        return panels

    def print(self) -> None:
        panels = self.get_panels()
        for panel in panels:
            print(panel)


def list_routes(
    blitz_app_name: Annotated[str, typer.Argument(..., help="Blitz app name")],
    model: Annotated[Optional[str], typer.Option()] = None,
    version: Annotated[Optional[str], typer.Option(help="Define the version of the app.")] = None,
) -> None:
    blitz = BlitzCore()
    try:
        blitz_app = blitz.get_app(blitz_app_name)
        if version is not None:
            blitz_app = blitz_app.get_version(Version.parse(version))
        blitz_app.load()
    except Exception as exc:
        print(f"[red bold]There is no blitz app named {blitz_app_name}[/red bold]")
        print("To list the available blitz apps run:")
        print("[bold]    blitz list[bold]")
        print(f"Error: {exc}")
        raise typer.Exit()
    if model:
        for resource in blitz_app.resources:
            if resource.config.name.lower() == model.lower():
                resources = [resource]
    else:
        resources = blitz_app.resources
    SwaggerPrinter(resources).print()
