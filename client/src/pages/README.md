# src / pages

## Purpose

This directory contains ***client side pages*** composed of (1) **html template file** which covers architecture and design of the pages, (2) **.ts class definition file** which covers logic, data, and controller, (3) **.scss file** to create css stylesheet files, (4) **module.ts file** which describe the architecture of the module, and (5) other files including **.guard.ts**, **.resolver.ts**, and so on.

Each directory can contain multiple pages. Each page will be prepared by *the triple* (.html, .scss, .ts). Sometimes, if no style is necessary, .scss file can be emitted.

Even if you can check the feature in local development environment (i.e., localhost:8100), it is not verifiable through the dev.heartsteps.net server directly. It should be ported to actual mobile app (i.e., iOS or Android) through mobile app build. This limits your test ability. Thus, it is crucial that you build a mobile app bundle with updated client codes.

## Description

* **baseline-week**: After onboarding process, baseline-week page will be shown instead of the app main screen. Duration of baseline week is determined by the server (participant.models.Study). Daily activity summary will be fetched and shown. 8 hours per day wearing Fitbit will take account into ***a day***. Fitbit-wearing days will be shown as filled bubbles. Not-wearing day will be shown as empty bubbles.