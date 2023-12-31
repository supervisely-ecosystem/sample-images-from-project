import os
from collections import defaultdict, namedtuple

import supervisely as sly

from dotenv import load_dotenv

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api.from_env()

SLY_APP_DATA_DIR = sly.app.get_data_dir()
SAMPLING_METHODS = {
    "Random": "Random images will be selected from the project no matter what classes they belong to.",
    "Stratified": "Images will be selected from each class proportionally to the number of images in the class.",
    "Custom": "You can manually set distribution of images for each class.",
}
ImageData = namedtuple("ImageData", ["info", "ann"])


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

        self.images_by_class = defaultdict(list)
        self.images = list()

    def get_project_info(self):
        self.project_info = api.project.get_info_by_id(self.selected_project)
        self.total_images_count = api.project.get_images_count(self.selected_project)
        self.project_meta = sly.ProjectMeta.from_json(
            api.project.get_meta(self.selected_project)
        )
        self.get_project_stats()
        self.get_images_by_class()

        if not self.images_by_class:
            sly.logger.info(
                f'Project "{self.project_info.name}" has no classes, will run retrieving function again.'
            )
            self.get_images_by_class(no_class=True)

    def get_project_stats(self):
        project_stats = api.project.get_stats(self.selected_project)["objects"]["items"]
        class_stats = {}

        for stat in project_stats:
            class_name = stat["objectClass"]["name"]
            class_stats[class_name] = {"total": stat["total"]}

        sly.logger.debug(f"Following class stats was saved in the state: {class_stats}")
        self.class_stats = class_stats

    def get_images_by_class(self, no_class: bool = False):
        dataset_ids = [
            dataset.id for dataset in api.dataset.get_list(self.selected_project)
        ]

        for dataset_id in dataset_ids:
            image_infos = api.image.get_list(dataset_id)

            anns = [
                sly.Annotation.from_json(ann_json, self.project_meta)
                for ann_json in api.annotation.download_json_batch(
                    dataset_id, [image_info.id for image_info in image_infos]
                )
            ]

            for image_info, ann in zip(image_infos, anns):
                image_data = ImageData(image_info, ann)

                if no_class:
                    self.images.append(image_data)
                else:
                    for label in ann.labels:
                        self.images_by_class[label.obj_class.name].append(image_data)

        if not no_class:
            sly.logger.debug(
                f"Saved {len(self.images_by_class)} (class_name, [(image_id, image_name)]) images in the state."
            )
        else:
            sly.logger.debug(
                f"Saved {len(self.images)} images in the state, since the project has no classes."
            )


STATE = State()
