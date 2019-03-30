import { NgModule } from "@angular/core";
import { FitbitWatchService } from "./fitbit-watch.service";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { WatchSetupComponent } from "./watch-setup.component";


@NgModule({
    declarations: [
        WatchSetupComponent
    ],
    entryComponents: [
        WatchSetupComponent
    ],
    exports: [
        WatchSetupComponent
    ],
    imports: [
        InfrastructureModule
    ],
    providers: [
        FitbitWatchService
    ]
})
export class FitbitWatchModule {}
