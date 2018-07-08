import { Component} from '@angular/core';

@Component({
  selector: 'onboard-end',
  templateUrl: 'onboard-end.html',
})
export class OnboardEndPane {
  constructor() {}

  sendHome() {
    console.log("Mark onboarding as complete!");
  }

}
