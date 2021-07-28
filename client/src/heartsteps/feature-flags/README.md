# How to use FeatureFlag (to be continuously updated)

## In the Client (Angular, typescript)

### Design Pattern #1: making it as a member variable

* Include the following three lines at the top of the file:

```
import { Subscription } from "rxjs";
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
```

* Add **featureFlagSubscription** member variable into the class
```
...
private featureFlagSubscription: Subscription;
...
```

* Add **featureFlagService** member variable, and initialize both member variables in the constructor.

```
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
```

* Otherwise, you can use the **this.featureFlagService** somewhere else.
```
    // in the class implementation
    public hasFlagX(): boolean {
        return this.featureFlagService.hasFlag('X');
    }
```

### Design Pattern #2: one-time use
* Include the following three lines at the top of the file:

```
import { Subscription } from "rxjs";
import { skip } from 'rxjs/operators';
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";
```

* Add **featureFlagSubscription** member variable into the class
```
...
private featureFlagSubscription: Subscription;
...
```

* Add **featureFlagService** member variable, and initialize both member variables in the constructor. When initializing, you need to subscribe it with a one-time handler. (finishing with ***.unsubscribe()***) In this case, the first default value from the ***BehaviorSubject*** class should be ignored. (by ***.pipe(skip(1))***)

```
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
```



## In the Server (Django, python)
* ***to be updated***