import {
    async,
    ComponentFixture,
    TestBed
} from '@angular/core/testing';
import { MyApp } from './app.component';
import { IonicModule, Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { ParticipantService, Participant } from '@heartsteps/participants/participant.service';
import { RouterModule, Router } from '@angular/router';
import { HomePageModule } from '@pages/home/home.module';
import { AppService } from './app.service';
import { BehaviorSubject } from 'rxjs';

class ParticipantServiceMock {
    public participant: BehaviorSubject<Participant> = new BehaviorSubject(undefined);
}

class AppServiceMock {

}

class RouterMock {

}

describe('MyApp', () => {
    let component: MyApp;
    let fixture: ComponentFixture<MyApp>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [MyApp],
            imports: [
                RouterModule.forRoot([]),
                HomePageModule,
                IonicModule.forRoot(MyApp)
            ],
            providers: [
                StatusBar,
                SplashScreen,
                { provide: Router, useClass: RouterMock },
                { provide: ParticipantService, useClass: ParticipantServiceMock },
                { provide: AppService, useClass: AppServiceMock },
            ]
        });
        fixture = TestBed.createComponent(MyApp);
        component = fixture.componentInstance;
    }))

    test('should exist', () => {
        expect(component).toBeDefined();
    })
});