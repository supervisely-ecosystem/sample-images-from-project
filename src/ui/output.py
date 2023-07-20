from typing import Optional
from datetime import datetime
import supervisely as sly

from random import sample, choice

from supervisely.app.widgets import (
    Container,
    Card,
    DestinationProject,
    Button,
    ProjectThumbnail,
    Progress,
    Text,
    Table,
    Field,
)

import src.globals as g

preview_table = Table(width=300)
preview_tooltip = Text(
    text=(
        "The result of sampling may be significantly different from the values in "
        "this table because of duplication, small sample size, incorrect class distribution or other factors."
    ),
    status="info",
)
preview_table_field = Field(
    title="Approximate sample distribution",
    # description="This table shows the approximate distribution of images with specific class in the sample.",
    content=Container([preview_tooltip, preview_table]),
)
preview_table_field.hide()

destination = DestinationProject(
    workspace_id=g.STATE.selected_workspace, project_type="images"
)

start_button = Button("Start sampling", icon="zmdi zmdi-play")
stop_button = Button("Stop sampling", button_type="danger", icon="zmdi zmdi-stop")
stop_button.hide()

progress = Progress()
progress.hide()

result_text = Text()
result_text.hide()

project_thumbnail = ProjectThumbnail()
project_thumbnail.hide()

card = Card(
    title="3️⃣ Output",
    description="Choose the destination for the sample and start the generation.",
    content=Container(
        [
            preview_table_field,
            destination,
            start_button,
            progress,
            result_text,
            project_thumbnail,
        ]
    ),
    content_top_right=stop_button,
    lock_message="Lock settings on step 2️⃣.",
    collapsable=True,
)
card.lock()
card.collapse()


def build_preview_table():
    columns = ["CLASS NAME", "NUMBER OF IMAGES"]
    rows = []
    total = 0
    for class_name, percentage in g.STATE.class_distribution.items():
        images_number = round(g.STATE.images_in_sample * percentage / 100)
        rows.append([class_name, images_number])
        total += images_number

    preview_table.read_json(
        {"columns": columns, "data": rows, "summaryRow": ["Total", total]}
    )

    preview_table_field.show()


def clear_preview_table():
    preview_table.read_json({"columns": [], "data": [], "summaryRow": []})
    preview_table_field.hide()


def prepare_samples():
    if g.STATE.sampling_method == "Random":
        all_images = []
        for class_name, images in g.STATE.images_by_class.items():
            all_images.extend(images)

        samples = sample(all_images, g.STATE.images_in_sample)

        sly.logger.debug(
            f"Random method is selected, {len(samples)} random images was sampled."
        )

        return samples

    samples = []
    for class_name, percentage in g.STATE.class_distribution.items():
        images_number = round(g.STATE.images_in_sample * percentage / 100)
        for _ in range(images_number):
            image = choice(g.STATE.images_by_class[class_name])
            if image not in samples:
                samples.append(image)
            else:
                sly.logger.debug(
                    f"Image {image.name} was skipped because of duplication."
                )
                g.STATE.skipped_images.append(image)

    sly.logger.debug(
        f"Stratified or Custom method is selected, {len(samples)} images was sampled."
    )

    return samples


@start_button.click
def start_sampling():
    samples = prepare_samples()

    if not samples:
        # TODO: add error message
        return

    project_id = destination.get_selected_project_id()
    dataset_id = destination.get_selected_dataset_id()

    result_text.hide()
    project_thumbnail.hide()

    start_button.text = "Sampling..."
    stop_button.show()

    sly.logger.debug(
        f"Readed values from destination widget. "
        f"Project ID: {project_id}, dataset ID: {dataset_id}."
    )

    if not project_id:
        sly.logger.debug("Project ID is not specified, creating a new project.")
        project_id = create_project(destination.get_project_name())
    if not dataset_id:
        sly.logger.debug("Dataset ID is not specified, creating a new dataset.")
        dataset_id = create_dataset(project_id, destination.get_dataset_name())

    g.api.project.update_meta(project_id, g.STATE.project_meta)

    progress.show()

    with progress(message="Uploading images...", total=len(samples)) as pbar:
        for batched_samples in sly.batched(samples):
            if not g.STATE.continue_sampling:
                sly.logger.debug("Stop button was clicked, stopping generation.")
                break

            uploaded_ids = g.api.image.upload_ids(
                dataset_id=dataset_id,
                names=[_.name for _ in batched_samples],
                ids=[_.id for _ in batched_samples],
                metas=[_.meta for _ in batched_samples],
            )

            g.api.annotation.upload_anns(
                img_ids=[_.id for _ in uploaded_ids],
                anns=[_.ann for _ in batched_samples],
            )

            sly.logger.info(f"Uploaded {len(batched_samples)} images.")
            pbar.update(len(batched_samples))

    sly.logger.info("Sampling is finished.")

    if g.STATE.continue_sampling:
        result_text.text = "Successfully sampled images."
        result_text.status = "success"

    else:
        result_text.text = "The sampling was stopped before the end."
        result_text.status = "warning"

    result_text.show()
    project_thumbnail.set(g.api.project.get_info_by_id(project_id))
    project_thumbnail.show()

    start_button.text = "Start sampling"
    stop_button.hide()
    stop_button.loading = False
    stop_button.text = "Stop sampling"


@stop_button.click
def stop_generation():
    stop_button.text = "Stopping..."
    stop_button.loading = True
    g.STATE.continue_sampling = False


def create_project(project_name: Optional[str]) -> int:
    if not project_name:
        project_name = f"{g.STATE.project_info.name} (sample)"

    project = g.api.project.create(
        g.STATE.selected_workspace, project_name, change_name_if_conflict=True
    )
    return project.id


def create_dataset(project_id: int, dataset_name: Optional[str]) -> int:
    if not dataset_name:
        dataset_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (sample)"

    dataset = g.api.dataset.create(
        project_id, dataset_name, change_name_if_conflict=True
    )
    return dataset.id
