import { Component, Output, EventEmitter } from "@angular/core";
import { FitbitWatchService } from "./fitbit-watch.service";
import { BrowserService } from "@infrastructure/browser.service";


@Component({
    selector: 'heartsteps-watch-setup',
    templateUrl: './watch-setup.component.html'
})
export class WatchSetupComponent {

    @Output('saved') saved: EventEmitter<boolean> = new EventEmitter();

    constructor(
        private fitbitWatchService: FitbitWatchService,
        private browserService: BrowserService
    ) {}

    public openFitbitPage() {
        const url = 'https://gam.fitbit.com/gallery/clock/0bd06f9e-2adc-4391-ab05-d177dda1a167';
        this.browserService.open(url);
    }

    public markDone() {
        this.fitbitWatchService.markInstalled()
        .then(() => {
            this.saved.emit(true);
        });
    }

}
