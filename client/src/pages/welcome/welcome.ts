import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { IonicPage, NavController, ModalController } from 'ionic-angular';
import { EnrollmentModal } from '@heartsteps/enrollment/enroll';
import { Router } from '@angular/router';

@Component({
  selector: 'page-welcome',
  templateUrl: 'welcome.html',
  entryComponents: [
    EnrollmentModal
  ]
})
export class WelcomePage implements OnInit {

  constructor(
    private el:ElementRef,
    private renderer:Renderer2,
    private modalCtrl: ModalController,
    private router: Router
  ) {}

  goToEnrollPage() {
    let modal = this.modalCtrl.create(EnrollmentModal);
    modal.onDidDismiss(()=> {
      this.router.navigate(['']);
    })
    modal.present();
  }

  ngOnInit() {
    this.renderer.addClass(this.el.nativeElement, 'start-screen')
  }

}
