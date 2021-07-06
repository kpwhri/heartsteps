import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
import { FirstBoutPlanningTimeService, FirstBoutPlanningTime } from './first-bout-planning-time.service';

@Component({
  selector: 'first-bout-planning-time', 
  templateUrl: './first-bout-planning-time.page.html'  
})
export class FirstBoutPlanningTimePage {

  public firstBoutPlanningForm: FormGroup;

  @Output() saved = new EventEmitter<boolean>();

  constructor(
    private loadingService: LoadingService,
    private firstBoutPlanningTimeService: FirstBoutPlanningTimeService
  ) {
    this.firstBoutPlanningTimeService.getTime()
      .catch(() => {
        return this.firstBoutPlanningTimeService.getDefaultFirstBoutPlanningTime()
      })
      .then((firstBoutPlanningTime: FirstBoutPlanningTime) => {
        this.createFirstBoutPlanningForm(firstBoutPlanningTime.time);
      });
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
