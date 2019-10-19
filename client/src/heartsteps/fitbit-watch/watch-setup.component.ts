import { Component, Output, EventEmitter } from "@angular/core";
import { FitbitWatchService } from "./fitbit-watch.service";

@Component({
    selector: 'heartsteps-watch-setup',
    templateUrl: './watch-setup.component.html'
})
export class WatchSetupComponent {

    @Output('saved') saved: EventEmitter<boolean> = new EventEmitter();

    constructor(
        private fitbitWatchService: FitbitWatchService
    ) {}

    public openFitbitPage() {
        this.fitbitWatchService.openWatchInstallPage();
    }

    public markDone() {
        this.saved.emit(true);
    }

}
