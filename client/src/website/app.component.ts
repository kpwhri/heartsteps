import { Component } from '@angular/core';

@Component({
    templateUrl: 'app.html'
})
export class HeartstepsWebsite {

    showDashboard: boolean = false;

    constructor() {
        console.log('This is the website!!');
    }
}
