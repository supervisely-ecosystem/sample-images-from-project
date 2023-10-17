import yaml
from typing import Optional
from supervisely.app.widgets import (
    Text,
    Card,
    Select,
    InputNumber,
    Editor,
    Field,
    Button,
    Container,
    Flexbox,
)

import supervisely as sly

import src.globals as g
import src.ui.output as output

sample_type_select = Select(
    items=[Select.Item("Percentage"), Select.Item("Number of images")]
)
sample_size_percentage_input = InputNumber(
    value=10, min=1, max=100, step=1, size="medium"
)
sample_size_number_input = InputNumber(value=10, min=1, step=1, size="medium")
sample_size_number_input.hide()

sample_size_flexbox = Flexbox(
    widgets=[sample_type_select, sample_size_percentage_input, sample_size_number_input]
)

sample_size_field = Field(
    title="Sample size",
    description="Select the sample size in percentage or number of images.",
    content=sample_size_flexbox,
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

lock_settings_button = Button("Save settings", icon="zmdi zmdi-lock")
unlock_settings_button = Button("Change settings", icon="zmdi zmdi-lock-open")
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


def sample_size_changed(sample_size):
    sampling_method = sampling_method_select.get_value()

    if sampling_method is not None and sampling_method == "Custom":
        sample_size = get_sample_size()

        update_custom_editor(sample_size)


sample_size_number_input.value_changed(sample_size_changed)
sample_size_percentage_input.value_changed(sample_size_changed)


def update_custom_editor(sample_size: Optional[int] = None):
    lock_settings_button.loading = True

    if not sample_size:
        sample_size = get_sample_size()

    calculate_maximum_percentage(sample_size)
    percentages = distribute_percentages(len(g.STATE.class_stats))

    editor_text = (
        f"# Total images count in sample: {g.STATE.images_in_sample}\n\n"
        "distribution: # In percentage\n"
    )
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

    output.total_percentage_text.hide()
    output.bad_distribution_text.hide()

    g.STATE.sampling_method = sampling_method

    g.STATE.sample_size = get_sample_size()

    g.STATE.images_in_sample = round(
        g.STATE.sample_size * g.STATE.total_images_count / 100
    )

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

        distribution_changed = False
        for class_name, class_distribution in g.STATE.class_distribution.items():
            if (
                class_distribution
                > g.STATE.class_stats[class_name]["maximum_percentage"]
            ):
                g.STATE.class_distribution[class_name] = g.STATE.class_stats[
                    class_name
                ]["maximum_percentage"]

                distribution_changed = True

            elif class_distribution < 0:
                g.STATE.class_distribution[class_name] = 0

                distribution_changed = True

        if distribution_changed:
            output.bad_distribution_text.text = (
                "At least one class percentage is more than maximum or less than 0. "
                "Bad percentages was changed to maximum or 0, which can impact the sample result."
            )
            output.bad_distribution_text.show()

        total_percentage = sum(g.STATE.class_distribution.values())

        if total_percentage != 100:
            output.total_percentage_text.text = (
                f"Total percentage {total_percentage} specified in parameters is not 100. "
                "The sample result may be different from the expected."
            )
            output.total_percentage_text.show()

        output.build_preview_table()

    elif sampling_method == "Stratified":
        total_class_images = sum(
            [class_dict["total"] for class_dict in g.STATE.class_stats.values()]
        )
        distribution = {}
        for class_name, class_dict in g.STATE.class_stats.items():
            percentage = round(class_dict["total"] * 100 / total_class_images)
            distribution[class_name] = percentage

        g.STATE.class_distribution = distribution

        output.build_preview_table()

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

    output.clear_preview_table()

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


def get_sample_size():
    if sample_type_select.get_value() == "Percentage":
        return sample_size_percentage_input.get_value()

    sample_size = int(
        (sample_size_number_input.get_value() / g.STATE.total_images_count) * 100
    )

    sample_size = sample_size if sample_size <= 100 else 100
    return sample_size


@sample_type_select.value_changed
def sample_type_changed(sample_type):
    if sample_type == "Percentage":
        sample_size_percentage_input.show()
        sample_size_number_input.hide()
    else:
        sample_size_percentage_input.hide()
        sample_size_number_input.show()
