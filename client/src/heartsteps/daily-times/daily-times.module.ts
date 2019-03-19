import { NgModule } from "@angular/core";
import { DailyTimeService } from "./daily-times.service";


@NgModule({
    providers: [
        DailyTimeService
    ]
})
export class DailyTimesModule {}
