import { NgModule } from "@angular/core";
import { InfrastructureModule } from "@infrastructure/infrastructure.module";
import { AntiSedentaryService } from "./anti-sedentary.service";



@NgModule({
    imports: [
        InfrastructureModule
    ],
    providers: [
        AntiSedentaryService
    ]
})
export class AntiSedentaryModule {}