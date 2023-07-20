import os

import supervisely as sly

from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))
api: sly.Api = sly.Api.from_env()

SLY_APP_DATA_DIR = sly.app.get_data_dir()
SAMPLING_METHODS = {
    "Random": "Random images will be selected from the project no matter what classes they belong to.",
    "Stratified": "Images will be selected from each class proportionally to the number of images in the class.",
    "Custom": "You can manually set distribution of images for each class.",
}


class State:
    def __init__(self):
        self.selected_team = sly.io.env.team_id()
        self.selected_workspace = sly.io.env.workspace_id()
        self.selected_project = sly.io.env.project_id(raise_not_found=False)
        self.project_info = None
        self.total_images_count = None

        self.continue_sampling = True

        self.sampling_method = None
        self.sample_size = None
        self.images_in_sample = None
        self.class_stats = None
        self.class_distribution = None

    def get_project_info(self):
        self.project_info = api.project.get_info_by_id(self.selected_project)
        self.total_images_count = api.project.get_images_count(self.selected_project)
        self.project_meta = sly.ProjectMeta.from_json(
            api.project.get_meta(self.selected_project)
        )
        self.get_project_stats()

    def get_project_stats(self):
        project_stats = api.project.get_stats(self.selected_project)["objects"]["items"]
        class_stats = {}

        for stat in project_stats:
            class_name = stat["objectClass"]["name"]
            class_stats[class_name] = {"total": stat["total"]}

        sly.logger.debug(f"Following class stats was saved in the state: {class_stats}")
        self.class_stats = class_stats


STATE = State()
