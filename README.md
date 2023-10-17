<div align="center" markdown>
<img src="https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275804519-dab5aad7-331d-45f3-9c79-cf4d7b677e00.png"/>

# Placeholder for app short description

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Sampling-methods">Sampling methods</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Sampling">Sampling</a> •
  <a href="#Acknowledgement">Acknowledgement</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/sample-images-from-project)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/sample-images-from-project)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/sample-images-from-project.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/sample-images-from-project.png)](https://supervise.ly)

</div>

## Overview

This application allows you to create samples from images project with three different sampling methods: random, stratified and custom.
In all methods it's possible to use percentage or number of images to create sample. The will create a new project with samples and will not change the original project.

## Sampling methods

The application supports three sampling methods, but strarified and custom methods only available if original project contain labeled images. If the project does not contain labeled images, only random sampling is available.

1. **Random method:** it is the simplest method. It randomly selects the required number of images from the project and creates a new project with them.

2. **Stratified method:** it is a method which will create a sample with the same distribution of classes as in the original project. It is useful when you need to create a sample where the original distribution of classes is preserved. For example, if you have a project with 100 images, 50 of which are cats and 50 are dogs, and you need to create a sample of 10 images, then the sample will contain 5 cats and 5 dogs.

3. **Custom method:** when using the custom method, you can specify the distribution of classes in the sample. For example, if you have a project with 100 images, 50 of which are cats and 50 are dogs, and you need to create a sample of 10 images, where 8 of them are cats and 2 are dogs, you need to specify the corresponding distribution: 80% for images with cats and 20% for images with dogs.

Detailed iformation about all methods you can find in the [Sampling](#Sampling) section.

## How To Run

The application can be launch from two context menus: Images Project and the Ecosystem. In the first case, the application will be launched with the selected project, in the second case you will need to select the project in the application interface.

### Launch from context menu of images project

**Step 1:** Run the application.

![search-in-ecosystem](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852319-f9829567-8cfd-4f5f-a7f4-01123e98ec76.png)

**Step 2:** Select the project from which you want to create a sample.

**Step 3:** Press the `Run` button.

![select-project](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852333-909fd78d-7c14-4efb-8808-1f2579a7bacf.png)

### Launch from the Ecosystem

**Step 1:** Run the application.

**Step 2:** Change the `Input type` parameter to `Ecosystem`.

![ecosystem](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852366-3dcfde91-be10-4890-95a3-54967699875a.png)

**Step 3:** Press the `Run` button.

## Sampling

**Step 1️:** Select the input project.

If you launched the application from the context menu of the images project, then the project will be selected automatically. Otherwise, you will need to select the project in the Section 1️⃣ and press the `Load data` button.

![load-data](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852419-8bfc7808-d242-4a26-bf63-782e0f7c12a1.png)

When the project is selected, you're ready to go to the next step.

![project-selected](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852454-0c92710f-8b85-46d0-85b9-f100ee4be326.png)

**Step 2️:** Specify the sample size.

Sample size can be specified in two ways: by `Percentage` or by `Number of images`. Use the widgets to select the type of sample size and specify the value.

![sample-size](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852507-72e03b98-ce2a-40d1-b553-2f8ddc06a618.png)

**Step 3️:** Select the sampling method.

As mentioned above, the application supports three sampling methods: random, stratified and custom. Let's consider each of them in more detail.

### Random method

Select `Random` in the `Sampling method` widget and basically you're done. The application will randomly select the required number of images from the project and create a new project with them.

![random](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852528-c3e25d06-b9fe-49e6-a2a2-8c2c99e6b36b.png)

### Stratified method

ℹ️ If the project does not contain labeled images, you'll not be able to select the `Stratified` method.

Select `Stratified` in the `Sampling method` widget. You don't need to specify anything else, the application will create a sample with the same distribution of classes as in the original project.

![stratified](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852556-78fad0b9-172a-4912-b3fb-ac5073ab78da.png)

### Custom method

ℹ️ If the project does not contain labeled images, you'll not be able to select the `Custom` method.

Select `Custom` in the `Sampling method` widget. After it the `Class distribution` editor will appear. Use it to specify the distribution of classes in the sample. Let's have a closer look at the `Class distribution` editor.

Here's an example of what you can see here:

```yaml
# Total images count in sample: 10

distribution: # In percentage
  cat: 80 # Maximum: 100
  dog: 20 # Maximum: 100
```

`Total images count in sample` is the number of images that will be in the sample. It is calculated based on the settings from the Section 2️⃣.
In `distribution` you can find a list of classes in the original project with their distribution in the sample. These values you can change manually. The maximum value for each class is calculated automatically based on the total number of images in the sample and the number of images in the original project. If you will try to set a value greater than the maximum, the sample results may be different from the settings you specified.

Keep in mind that if the sum of all values in `distribution` will not be equal to 100, the results may be slightly different from what you expect.

![custom](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852587-e14840a4-9b7f-4e5a-9ca5-7d9b0fae84e7.png)

**Step 4️:** Press the `Save settings` button.

After the settings are saved, you can go to the final step. If you selected `Stratified` or `Custom` methods you will also see the `Approximate sample distribution` table. It shows the approximate number of images for each class in the sample. 

![approximate-sample-distribution](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852616-705896df-cc75-4025-a60e-b0cfce078ab5.png)

ℹ️ The actual number of images in the sample may differ from the values in the table for the following reasons:

1. If the image contains different classes, then it will be counted for each class.
2. If the sum of all values in `distribution` is not equal to 100.
3. If class distribution is greater than the maximum value for the class.
4. If the original project contains small number of images and / or small amount of images for specific class.
5. If the sample size is small.

**Step 5️:** Select the output project and dataset and press the `Run` button.

You can enter output project and dataset names manually or they will be generated automatically based on the input project name. 
Now press the `Start sampling` button and wait for the application to finish. You may also stop the process by clicking on the `Stop sampling` button.

After the application finishes, you will see the result project widget, which you can use to open the project.

![result-project](https://github-production-user-asset-6210df.s3.amazonaws.com/118521851/275852661-036d1373-7b67-4d58-9b41-e23c31636894.png)

## Acknowledgement

- [Stratified sampling](https://en.wikipedia.org/wiki/Stratified_sampling)