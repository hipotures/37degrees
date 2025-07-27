# Scene Description Template Guide for LLM

## sceneDescription
The root container that encapsulates all visual elements needed to describe a single scene from the book for image generation.

## title
A descriptive name for the scene that summarizes what's happening in this particular moment of the story.

## setting
This section provides the when and where of the scene - the contextual information that places the action in a specific time and location.

* **time** - The historical period and time of day when this scene occurs - ensures all elements like clothing, architecture, and objects are period-appropriate
* **location** - The geographical place where the action happens, including regional context - ensures architectural styles, vegetation, and cultural elements match the specified region
* **weather** - The atmospheric conditions that influence the scene's mood and visual appearance

## characters
An array describing each person visible in the scene, treating each as if the viewer has never seen them before.

* **appearance** - How the person looks physically - their gender, age, and distinguishing visual features
* **clothing** - What the person is wearing, appropriate to their time period and social status - must be consistent with the era and location specified in settings
* **position** - Where the person is located in the scene and their body posture
* **action** - What the person is doing at this moment - their gesture or activity

## scene
The main visual narrative section that describes what's happening and what can be seen.

* **mainElements** - The primary things happening or visible that define what this scene is about - all visual elements should be consistent with the established time period and location
* **details** - The smaller objects, props, and environmental features that make the scene feel authentic - all items should be historically and geographically accurate to the specified time and location
* **background** - What's visible behind the main action that provides context - architecture, landscape, and any visible elements should match the specified time period and geographical location
* **atmosphere** - The overall mood and feeling created by the visual elements

## composition
How the scene should be framed and presented visually.

* **cameraAngle** - The viewpoint from which we observe the scene
* **focus** - What element should draw the viewer's attention first
* **depth** - How visual elements are layered from foreground to background to create dimensional space