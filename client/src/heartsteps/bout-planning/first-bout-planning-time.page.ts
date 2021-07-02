import { Component, Output, EventEmitter } from '@angular/core';
import { FormControl, Validators, FormGroup } from '@angular/forms';

import { LoadingService } from '@infrastructure/loading.service';
// import { ReflectionTimeService, ReflectionTime } from './reflection-time.service';
import { FirstBoutPlanningTimeService, FirstBoutPlanningTime } from './first-bout-planning-time.service';
// import { SelectOption } from '@infrastructure/dialogs/select-dialog.controller';

@Component({
  selector: 'first-bout-planning-time', 
  templateUrl: './first-bout-planning-time.page.html'  
}) 

// export class WeeklyReflectionTimePage {
export class FirstBoutPlanningTimePage {

  // public weeklyReflectionForm: FormGroup;
  public firstBoutPlanningForm: FormGroup;
  // public days:Array<SelectOption> = [{
  //     'name': 'Saturday',
  //     'value': 'saturday'
  // }, {
  //     'name': 'Sunday',
  //     'value': 'sunday'
  // }];

  @Output() saved = new EventEmitter<boolean>();

  constructor(
    private loadingService: LoadingService,
    // private reflectionTimeService: ReflectionTimeService
    private firstBoutPlanningTimeService: FirstBoutPlanningTimeService
  ) {
    // this.reflectionTimeService.getTime()
    this.firstBoutPlanningTimeService.getTime()
      .catch(() => {
        // return this.reflectionTimeService.getDefaultReflectionTime()
        return this.firstBoutPlanningTimeService.getDefaultFirstBoutPlanningTime()
      })
      // .then((reflectionTime: ReflectionTime)=> {
      //   this.createReflectionForm(reflectionTime.day, reflectionTime.time);
      // });
      .then((firstBoutPlanningTime: FirstBoutPlanningTime) => {
        this.createFirstBoutPlanningForm(firstBoutPlanningTime.time);
      });
  }

  // createReflectionForm(day: string, time: Date) {
  createFirstBoutPlanningForm(time: Date) {
    // this.weeklyReflectionForm = new FormGroup({
    //     day: new FormControl(day, Validators.required),
    //     time: new FormControl(time, Validators.required)
    // })
    this.firstBoutPlanningForm = new FormGroup({
      time: new FormControl(time, Validators.required)
    })
  }

  save() {
    // if(this.weeklyReflectionForm.valid) {
    //     this.loadingService.show('Saving reflection time')
    //     this.reflectionTimeService.setTime(this.weeklyReflectionForm.value)
    //     .then(() => {
    //         this.saved.emit(true);                
    //     })
    //     .catch((error) => {

    //     })
    //     .then(() => {
    //         this.loadingService.dismiss()
    //     })
    // }
    if (this.firstBoutPlanningForm.valid) {
      this.loadingService.show('Saving first bout planning time')
      this.firstBoutPlanningTimeService.setTime(this.firstBoutPlanningForm.value)
        .then(() => {
          this.saved.emit(true);
        })
        .catch((error) => {

        })
        .then(() => {
          this.loadingService.dismiss()
        })
    }
  }


}
