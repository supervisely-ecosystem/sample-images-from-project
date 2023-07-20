import os

import supervisely as sly
from supervisely.app.widgets import (
    Card,
    SelectProject,
    Button,
    Container,
    ProjectThumbnail,
    Text,
)

import src.globals as g
import src.ui.settings as settings

select_project = SelectProject(workspace_id=g.STATE.selected_workspace)

project_thumbnail = ProjectThumbnail()
project_thumbnail.hide()

load_button = Button("Load data")
change_project_button = Button("Change project", icon="zmdi zmdi-lock-open")
change_project_button.hide()

no_project_message = Text(
    "Please, select a project before clicking the button.",
    status="warning",
)
no_project_message.hide()

if g.STATE.selected_project:
    # If the app was loaded from a project.
    sly.logger.debug("App was loaded from a project.")

    select_project.hide()
    load_button.hide()

    g.STATE.get_project_info()
    project_thumbnail.set(g.STATE.project_info)
    project_thumbnail.show()

    settings.card.unlock()
    settings.card.uncollapse()
else:
    sly.logger.debug("App was loaded from ecosystem.")

# Input card with all widgets.
card = Card(
    "1️⃣ Input project",
    "Images from the selected project will be loaded.",
    content=Container(
        widgets=[
            project_thumbnail,
            select_project,
            load_button,
            no_project_message,
        ]
    ),
    content_top_right=change_project_button,
    collapsable=True,
)


@load_button.click
def load_project():
    """Handles the load button click event. Reading values from the SelectProject widget,
    calling the API to get project, workspace and team ids (if they're not set),
    building the table with images and unlocking the rotator and output cards.
    """
    project_id = select_project.get_selected_id()

    if not project_id:
        # If the project id is empty, showing the warning message.
        no_project_message.show()
        return

    # Hide the warning message if project was selected.
    no_project_message.hide()

    # Changing the values of the global variables to access them from other modules.
    g.STATE.selected_project = project_id

    # Disabling the project selector and the load button.
    select_project.disable()
    load_button.hide()

    # Showing the lock checkbox for unlocking the project selector and button.
    change_project_button.show()

    g.STATE.get_project_info()

    project_thumbnail.set(g.STATE.project_info)
    project_thumbnail.show()

    settings.card.unlock()
    settings.card.uncollapse()

    card.lock()


def clean_static_dir():
    # * Utility function to clean static directory, it can be securely removed if not needed.
    static_files = os.listdir(g.STATIC_DIR)

    sly.logger.debug(
        f"Cleaning static directory. Number of files to delete: {len(static_files)}."
    )

    for static_file in static_files:
        os.remove(os.path.join(g.STATIC_DIR, static_file))


@change_project_button.click
def handle_input():
    card.unlock()
    select_project.enable()
    load_button.show()
    change_project_button.hide()
