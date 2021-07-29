import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
import { FirstBoutPlanningTimeService, FirstBoutPlanningTime } from './first-bout-planning-time.service';

import { SelectDialogController, SelectOption } from '@infrastructure/dialogs/select-dialog.controller';

@Component({
  selector: 'first-bout-planning-time',
  templateUrl: './first-bout-planning-time.page.html'
})
export class FirstBoutPlanningTimePage {

  public firstBoutPlanningForm: FormGroup;

  public times: Array<SelectOption> = [{
    'name': '4:00 am',
    'value': '4:00'
  }, {
    'name': '5:00 am',
    'value': '5:00'
  }, {
    'name': '6:00 am',
    'value': '6:00'
  }, {
    'name': '7:00 am',
    'value': '7:00'
  }, {
    'name': '8:00 am',
    'value': '8:00'
  }, {
    'name': '9:00 am',
    'value': '9:00'
  }, {
    'name': '10:00 am',
    'value': '10:00'
  }, {
    'name': '11:00 am',
    'value': '11:00'
  }, {
    'name': '12:00 pm',
    'value': '12:00'
    }];

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

  createFirstBoutPlanningForm(time: string) {
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
