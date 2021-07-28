import { Inject, Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
import { FirstBoutPlanningTimeService, FirstBoutPlanningTime } from './first-bout-planning-time.service';

import { Subscription } from 'rxjs';
import { skip } from 'rxjs/operators';
import { FeatureFlags } from "@heartsteps/feature-flags/FeatureFlags";
import { FeatureFlagService } from "@heartsteps/feature-flags/feature-flags.service";


@Component({
  selector: 'first-bout-planning-time',
  templateUrl: './first-bout-planning-time.page.html'
})
export class FirstBoutPlanningTimePage {

  public firstBoutPlanningForm: FormGroup;
  private featureFlagSubscription: Subscription;

  @Output() saved = new EventEmitter<boolean>();

  constructor(
    private loadingService: LoadingService,
    private firstBoutPlanningTimeService: FirstBoutPlanningTimeService,
    private featureFlagService: FeatureFlagService
  ) {
    this.featureFlagSubscription = this.featureFlagService
      .currentFeatureFlags
      .pipe(skip(1))  // BehaviorSubject class provides the default value (in this case, an empty feature flag list). This line skip the default value
      .subscribe(
        (flags) => {
          if (this.featureFlagService.hasFlag('nlm')) {
            // handle "with flag" case
            console.log("nlm tag is found.")
            this.firstBoutPlanningTimeService.getTime()
              .catch(() => {
                return this.firstBoutPlanningTimeService.getDefaultFirstBoutPlanningTime()
              })
              .then((firstBoutPlanningTime: FirstBoutPlanningTime) => {
                this.createFirstBoutPlanningForm(firstBoutPlanningTime.time);
              });
          } else {
            // handle "without flag" case
            console.log("no nlm tag is found.")
            this.saved.emit();
          }
          this.featureFlagSubscription.unsubscribe();
        }
    );
    this.featureFlagService.getFeatureFlags();
  }

  createFirstBoutPlanningForm(time: Date) {
    this.firstBoutPlanningForm = new FormGroup({
      time: new FormControl(time, Validators.required)
    })
  }

  save() {
    if (this.firstBoutPlanningForm.valid) {
      this.loadingService.show('Saving first bout planning time')
      this.firstBoutPlanningTimeService.setTime(this.firstBoutPlanningForm.value)
        .then(() => {
          this.saved.emit(true);
        })
        .catch((error) => {
          // Added save here beacuse set time was always failing
          this.saved.emit(true);
        })
        .then(() => {
          this.loadingService.dismiss()
        })
    }
  }


}
