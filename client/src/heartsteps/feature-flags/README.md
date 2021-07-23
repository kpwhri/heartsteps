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
* ***Can anybody think of the easier one-time use design pattern?***

## In the Server (Django, python)
* ***to be updated***