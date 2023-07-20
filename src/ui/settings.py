import yaml
from typing import List, Tuple, Optional
from supervisely.app.widgets import (
    Text,
    Card,
    Select,
    InputNumber,
    Editor,
    Field,
    Button,
    Container,
)

import supervisely as sly

import src.globals as g
import src.ui.output as output

sample_size_input = InputNumber(value=10, min=1, max=100, step=1)
sample_size_field = Field(
    title="Sample size",
    description="Select the sample percentage from 1 to 100.",
    content=sample_size_input,
)

sampling_method_select = Select(
    items=[Select.Item(method) for method in g.SAMPLING_METHODS.keys()],
)
sampling_method_select.set_value(None)
sampling_method_field = Field(
    title="Sampling method",
    description="Select how the sampling will be performed.",
    content=sampling_method_select,
)
sampling_method_hint = Text(status="info")
sampling_method_hint.hide()
no_method_message = Text("Sampling method must be selected.", status="warning")
no_method_message.hide()

lock_settings_button = Button("Lock settings", icon="zmdi zmdi-lock")
unlock_settings_button = Button("Unlock settings", icon="zmdi zmdi-lock-open")
unlock_settings_button.hide()


distribution_editor = Editor(language_mode="yaml", height_lines=50)
distribution_field = Field(
    title="Class distribution",
    description="Set the percentage of each class in the sample.",
    content=distribution_editor,
)
distribution_field.hide()


card = Card(
    title="2️⃣ Settings",
    description="Choose the sample size and additional parameters.",
    content=Container(
        [
            sample_size_field,
            sampling_method_field,
            sampling_method_hint,
            no_method_message,
            distribution_field,
            lock_settings_button,
        ]
    ),
    lock_message="Select the dataset on step 1️⃣.",
    content_top_right=unlock_settings_button,
    collapsable=True,
)
card.lock()
card.collapse()


@sampling_method_select.value_changed
def sampling_method_changed(method):
    sampling_method_hint.text = g.SAMPLING_METHODS[method]
    sampling_method_hint.show()
    no_method_message.hide()

    if method == "Custom":
        update_custom_editor()
    else:
        pass
        distribution_editor.set_text("")
        distribution_field.hide()


@sample_size_input.value_changed
def sample_size_changed(sample_size):
    sampling_method = sampling_method_select.get_value()

    if sampling_method is not None and sampling_method == "Custom":
        update_custom_editor(sample_size)


def update_custom_editor(sample_size: Optional[int] = None):
    lock_settings_button.loading = True

    if not sample_size:
        sample_size = sample_size_input.get_value()

    calculate_maximum_percentage(sample_size)
    percentages = distribute_percentages(len(g.STATE.class_stats))

    editor_text = "distribution:\n"
    for class_name, class_dict, percentage in zip(
        g.STATE.class_stats.keys(), g.STATE.class_stats.values(), percentages
    ):
        percentage = min(percentage, class_dict["maximum_percentage"])
        editor_text += f"  {class_name}: {percentage} # Maximum: {class_dict['maximum_percentage']}\n"

    distribution_editor.set_text(editor_text)
    distribution_field.show()
    lock_settings_button.loading = False


def calculate_maximum_percentage(sample_size):
    g.STATE.images_in_sample = round(sample_size * g.STATE.total_images_count / 100)

    sly.logger.debug(
        f"Number of images in the sample with sample size {sample_size}: {g.STATE.images_in_sample}"
    )

    for class_name, class_dict in g.STATE.class_stats.items():
        class_total = class_dict["total"]
        if class_total == 0:
            maximum_percentage = 0
        else:
            maximum_percentage = (
                round(class_total * 100 / g.STATE.images_in_sample)
                if g.STATE.images_in_sample > class_total
                else 100
            )

        g.STATE.class_stats[class_name]["maximum_percentage"] = maximum_percentage

    sly.logger.debug(
        f"Maximum percentages for each class was saved in the state: {g.STATE.class_stats}"
    )


@lock_settings_button.click
def lock_settings():
    sampling_method = sampling_method_select.get_value()
    if not sampling_method:
        no_method_message.show()
        return

    g.STATE.sampling_method = sampling_method
    g.STATE.sample_size = sample_size_input.get_value()

    sly.logger.info(
        f"Settings locked. Sampling method: {sampling_method}, sample size: {g.STATE.sample_size}"
    )

    if sampling_method == "Custom":
        g.STATE.class_distribution = yaml.safe_load(distribution_editor.get_text()).get(
            "distribution"
        )
        sly.logger.info(
            f"Custom method is selected. Distribution: {g.STATE.class_distribution}"
        )

    unlock_settings_button.show()

    output.card.unlock()
    output.card.uncollapse()

    card.lock()
    card.collapse()


@unlock_settings_button.click
def unlock_settings():
    g.STATE.sampling_method = None
    g.STATE.sample_size = None
    g.STATE.class_distribution = None

    unlock_settings_button.hide()

    output.card.lock()
    output.card.collapse()

    card.unlock()
    card.uncollapse()


def distribute_percentages(num_parts: int):
    quotient = 100 // num_parts
    remainder = 100 % num_parts

    parts = [quotient] * num_parts

    for i in range(remainder):
        parts[i] += 1

    return parts
