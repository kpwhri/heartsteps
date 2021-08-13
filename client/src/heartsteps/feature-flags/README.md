# How to use FeatureFlag (to be continuously updated)

## In the Client (Angular, typescript)

### Design Pattern #1: making it as a member variable

-   Include the following three lines at the top of the file:

          import { Subscription } from "rxjs";
          import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
          import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";

-   Add **featureFlagSubscription** member variable into the class

          ...
          private featureFlagSubscription: Subscription;
          ...

-   Add **featureFlagService** member variable, and initialize both member variables in the constructor.

          constructor(
              ... ,
              private featureFlagService: FeatureFlagService
          ) {
          ...
          this.featureFlagSubscription =
                  this.featureFlagService
                      .currentFeatureFlags
                      .subscribe(
                          (flags) => {
                              this.featureFlags = flags;

                              or

                              this.hasFlagX = this.featureFlagService.hasFlag('X');
                          }
                      );
                      ...
              this.featureFlagService.getFeatureFlags();  // FeatureFlagService is singleton model. Thus, if the service is created somewhere else before, the flag handler described above will be called after a few seconds. To prevent unneccesary delay, we may force to reload the flag.
          }

-   Otherwise, you can use the **this.featureFlagService** somewhere else.

          // in the class implementation
          public hasFlagX(): boolean {
              return this.featureFlagService.hasFlag('X');
          }

### Design Pattern #2: one-time use

-   Include the following four lines at the top of the file:

          import { Subscription } from "rxjs";
          import { skip } from 'rxjs/operators';
          import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
          import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";

-   Add **featureFlagSubscription** member variable into the class

          ...
          private featureFlagSubscription: Subscription;
          ...

-   Add **featureFlagService** member variable, and initialize both member variables in the constructor. When initializing, you need to subscribe it with a one-time handler. (finishing with **_.unsubscribe()_**) In this case, the first default value from the **_BehaviorSubject_** class should be ignored. (by **_.pipe(skip(1))_**)

          constructor(
              ... ,
              private featureFlagService: FeatureFlagService
          ) {
          ...
              this.featureFlagSubscription =
                  this.featureFlagService
                      .currentFeatureFlags
                      .pipe(skip(1))  // BehaviorSubject class provides the default value (in this case, an empty feature flag list). This line skip the default value
                      .subscribe(
                          (flags) => {
                              if (this.featureFlagService.hasFlag('X')) {
                                  // handle the case with the flag
                                  ...
                              } else {
                                  // handle the case without the flag
                                  ...
                              }
                          }
                          this.featureFlagSubscription.unsubscribe();
                      );
                      ...
              this.featureFlagService.getFeatureFlags();  // FeatureFlagService is singleton model. Thus, if the service is created somewhere else before, the flag handler described above will be called after a few seconds. To prevent unneccesary delay, we may force to reload the flag.
          }

### Detailed description of the Client use

The context of checking up on user-based featureFlag can be categorized into three:

1. **Optional UI** A UI component in an existing UI frame is shown if the featureFlag is set (or not set): NotificationCenter
2. **Algorithm Control** A UI component doesn’t change the appearance, but the logic inside of it depends on whether the featureFlag is set or not: no example yet
3. **Screen Change** The whole screen should be redirected to somewhere else (i.e., skipping a particular screen) if the featureFlag is set or not: First Bout Planning Window Hour

If we look into each one of them, they should be implemented slightly different.

1. **Optional UI**

In page/component constructor, you need to create an instance of FeatureFlagService as an Injection, subscribe to the currentFeatureFlag, and bind “show” and “unshow” logics inside the **_.subscribe()_** with **_this.featureFlagservice.hasFlag(‘X’)_**.

See this:

    private featureFlagSubscription: Subscription;
    …
    constructor(
            ... ,
            private featureFlagService: FeatureFlagService
        ) {
        ...
        this.featureFlagSubscription =
                this.featureFlagService
                    .currentFeatureFlags
                    .subscribe(
                        (flags) => {
                            if (this.featureFlagService.hasFlag('X')) {
                                // show the UI component
                                ...
                            } else {
                                // unshow the UI component
                                ...
                            }
                        }
                        this.featureFlagSubscription.unsubscribe();
                    );
                    ...
            this.featureFlagService.getFeatureFlags();  // FeatureFlagService is singleton model. Thus, if the service is created somewhere else before, the flag handler described above will be called after a few seconds. To prevent unnecessary delay, we may force to reload the flag.
        }

In this case, since it is an optional UI, you should be ready for the both transition: from unshown to shown, from shown to unshown. It’s because we don’t know the current status, and we don’t know the future status, either. Thus, both transitions should be implemented independently. If you mistakenly guess that you would be "unflagged", and you only implement the former, it might be buggy if the status changes in the server (regardless you want it or not).

Unsubscription is not always needed. However, if you don't want the UI component to change without any further user interaction after you load up the UI, you might want to unsubscribe it. Remember, the unsubscription can cause some discrepancy if you change the flag while the user is seeing the UI. Thus, you might want to check the flag again at the server-side if necessary.

The last line (**_.getFeatureFlag()_**) is intended to be used in the context of dynamic screen navigation. If the FeatureFlagService is created somewhere else, the service might keep asking continously the server if the user has the flag or not, every 10 seconds. If this class is constructed (i.e., the current screen is loaded) in the middle of that 10 seconds, next refreshing of the flag will be a few seconds later. To avoid those delay, you might want to force the refresh **RIGHT NOW**. It will cause an additional server request, but the server will be fine. :)

As Nick mentioned, this usecase might be replaced by Angular directives. That should be the next update for this document.

2. **Algorithm Control**

In this case, I assume that the algorithm works under the hood without any UI change. (i.e., think about a single button) In that case, the UI (i.e., button) should work instantaneously. Thus, the flag should be fetched in the constructor. The result of the flag should be stored in the class member variable.

See also:

    private featureFlagSubscription: Subscription;
    private flagX: boolean;

    …
    constructor(
            ... ,
            private featureFlagService: FeatureFlagService
        ) {
        ...
        this.flagX = false; // or any other default value you want
        this.featureFlagSubscription =
                this.featureFlagService
                    .currentFeatureFlags
                    .pipe(skip(1))  // BehaviorSubject class provides the default value (in this case, an empty feature flag list). This line skip the default value
                    .subscribe(
                        (flags) => {
                            this.flagX = this.featureFlagService.hasFlag('X');
                        }
                        this.featureFlagSubscription.unsubscribe();
                    );
                    ...
            this.featureFlagService.getFeatureFlags();  // FeatureFlagService is singleton model. Thus, if the service is created somewhere else before, the flag handler described above will be called after a few seconds. To prevent unnecessary delay, we may force to reload the flag.
        }

Then you can use the **_this.flagX_** anywhere else in the class.

Remember, fetching the flag is not "right away" task. Thus, you need to be prepared for the case you **don't** know the answer yet. For those cases, you might want to make the logic more complicated (i.e., creating another variable denoting if the fetch is complete or not).

Unlike the usecase 1, this one-time assignment should be handled with care. Thus, you need to skip the first default update from the subscription. BehaviorSubject class always send the first default value (before any update). In our use case, the default value is critical since we use the value for the control, and we have to unsubscribe after that. This skipping ensures us to get the right value with slight delay. The reason why the delay is short is that we forcefully refresh the flag at the end of the constructor (**_.getFeatureFlags()_**).

You might want to _some_ initial tasks right after you got the flag result. In that case, unlike the optional UI usecase, you can prepare for only one direction (i.e., default -> !default).

It seems not easy to replace this usecase with Angular directives. However, whoever does that, please update this documentation.

3. **Screen Change**

Screen navigation is sometimes trickier than anything. If the current or next screen has own navigational tools (i.e., back button), it will be even trickier.

After numerous experiments, I would suggest not to actively use featureFlag for the screen change **_INSIDE THE SCREEN_**. The reason for this is, the scope you need to change expands dramatically and it is unpredictable. I'll explain in detail.

Let's say, you have an optional screen 'B' between 'A' and 'C'. The sequence would be like this:

|               Flag                | Screen Sequence |
| :-------------------------------: | :-------------: |
|     if the user has flag 'X'      |   A -> B -> C   |
| if the user doesn't have flag 'X' |     A -> C      |

If you use featureFlag in the B's constructor (i.e., usecase 1 or 2), it works. If the user doesn't have flag X, you can put something like "**_this.skip()_**" or "**_this.go('C')_** in the **_subscribe()_**. However, you will experience difficulties to control external navigation. For example, let's assume 'C' has **_back_** button. If the user doesn't have flag 'X', what would be the expected behavior of that button?

Of course, the button has to reroute the user to screen A. But it is not easy. You might want to check if the previous screen is A or C then use it to decide the argument of 'skip' function in the subscribe. (e.g., if you proceed from A to B to C, skipping means B->C. if you came back from C to B by clicking the back button, skipping means B->A.)

Another option would be changing C. If the flag 'X' is given, we can change the logic of 'back' button of C. However, most navigational tools are not argumentable. They are implemented simply in the directives. And, what if B is not the only previous screen of C? What if there's another sequence of D->C?

Thus, using featureFlag in the screen B is not an option. You need to create (or use) a **superstructure** of the pages. If there is no superstructure for the UI sequence, you need to make it. If there is, you can use it.

So, you add featureFlagService in the superstructure's constructor. And use the flag information to decide the sequence of the pages. Remember, screen navigation takes a while (even days in some cases). So it should be well-tested. (particularly, try to chnage the flag during the screen navigation.)

In heartsteps client, **_heartsteps-stepper_** directive works as a superstructure. You need to provide "**[steps]**" argument to the directive, which means the sequence of the screen. In the **.ts** file, you can change the sequence of the steps depending on the flag.

One good follow-up question is "**how to avoid hardcoding**". We need some more time to answer that question.

## In the Server (Django, python)

Feature flags can be added or removed to a Study. When feature flags are added, they will be applied to all participants within that Study. When feature flags are removed, they are removed from all participants in that study. Participant-level feature flags (flags not included in the study-wide feature flags, usually unique to a participant or cohort) will not be added or removed by adding and removing study-wide feature flags. For the purpose of this documentation we will call such participant-level flags unique.

### Example

old studywide list = ['hi', 'hello', 'wow']

new studywide list = ['hi', 'wow', 'yikes']

current stored feature flags list for user = ['hi', 'hello', 'wow', 'a_unique_flag']

final flag to be used in update = ['hi', 'wow', 'yikes', 'a_unique_flag']

### Edge Cases and Common Pitfalls

The only exception to this rule is if you convert a unique participant-level feature flag to a global, study-wide feature flag. For example, let's say you update study-wide feature flags like so:

#### First edit

old studywide list = ['hi', 'hello', 'wow']

new studywide list = ['hi', 'wow', 'yikes', 'not_so_unique_flag']

current stored feature flags list for user = ['hi', 'hello', 'wow', 'not_so_unique_flag']

final flag to be used in update = ['hi', 'wow', 'yikes', 'not_so_unique_flag']

#### Second edit

old studywide list = ['hi', 'wow', 'yikes', 'not_so_unique_flag']

new studywide list = ['hi', 'wow', 'yikes']

current stored feature flags list for user = ['hi', 'wow', 'yikes', 'not_so_unique_flag']

final flag to be used in update = ['hi', 'wow', 'yikes']

You've effectively deleted 'not_so_unique_flag' for all users in that Study. Be careful when naming new study-wide feature flags so that they don't overlap with existing unique flags.

### Deleting unique participant-level flags in bulk

This "pitfall" can also be exploited to delete a unique participant-level flag en masse. Say you've lost track of how many participants have a unique flag called 'impulsively_assigned_flag' and you want to delete all references of the flag from all participants of a study. If you first made the flag a study-wide flag (applying it to everyone in the study) and then delete the flag from the study-wide flag list it will delete all mentions of the flag. This interface for deleting unique flags will likely be improved in the future.

### Adding study-wide feature flags

To add study-wide flags go to `heartsteps.net/admin` and then click "Studies" under the Participants subheading. Click the study you would like to change and then under "Studywide feature flags" add flags in a comma-delimited string format. For example, if you wanted the flags flag1, flag2 and flag3, you would write "flag1, flag2, flag3" (without the quotes). Each flag is delimited with a comma and a space. Then click save on the bottom.

### Removing study-wide feature flags

To remove study-wide feature flags, go to `heartsteps.net/admin` and then click "Studies" under the Participants subheading. Click the study you would like to change and then under "Studywide feature flags" remove flags by removing them from the comma-delimited list. Be sure to keep the same comma-delimited format. For example, if the current study-wide flags list was "hi, hello, wow" and you wanted to remove "hello" you would change the list to "hi, wow" not "hi,, wow" or "hi, , wow". Similarly, if you wanted to remove "hi" and "wow", your final list would be "hello" not ", hello, ". Once finished, click save on the bottom.

### Sanity check

To be sure your flags have been applied across all users in your study, you can go back to `heartsteps.net/admin`, click "Feature Flags" and then find a participant in your study. Click on the participant and under "Flags" you should see all of your study-wide feature flags along with that participant's unique flags if they have any.
