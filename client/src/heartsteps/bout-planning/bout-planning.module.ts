import { NgModule } from "@angular/core";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { BoutPlanningService } from "./bout-planning.service";



@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        BoutPlanningService
    ]
})
export class BoutPlanningModule {}