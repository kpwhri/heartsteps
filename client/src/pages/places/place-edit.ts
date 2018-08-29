import { Component, ViewChild, ElementRef } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { Geolocation } from '@ionic-native/geolocation';

declare var google;

@Component({
    selector: 'place-edit',
    templateUrl: 'place-edit.html'
})
export class PlaceEdit {

    private address:String
    private type:String

    private latitude:Number
    private longitude:Number

    private mapLat:Number
    private mapLng:Number

    @ViewChild('map') mapElement: ElementRef
    private map:any
    private mapMarker:any

    private geocoder:any

    private geocoderTimeout:any
    private autocompletionService:any
    private addressPredictions:Array<any>

    private currentLocation:any

    private updateView:boolean

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
        private geolocation:Geolocation
    ) {
        const location = params.get('location')
        if(location) {
            this.address = location.address
            this.latitude = location.lat
            this.longitude = location.lng
            this.updateView = true
        } else {
            this.updateView = false
        }

        this.autocompletionService = new google.maps.places.AutocompleteService()
        this.geocoder = new google.maps.Geocoder()
    }

    ionViewDidLoad() {
        this.loadMap()
        if(this.latitude && this.longitude) {
            this.placeMapPin(this.latitude, this.longitude)
        }
    }

    dismiss() {
        this.viewCtrl.dismiss()
    }

    update() {
        this.viewCtrl.dismiss({
            address: this.address,
            latitude: this.latitude,
            longitude: this.longitude
        })
    }

    delete() {
        this.viewCtrl.dismiss(false)
    }

    showPredictions() {
        if(this.geocoderTimeout) {
            clearTimeout(this.geocoderTimeout)
        }

        this.geocoderTimeout = setTimeout(() => {
            this.geocoderTimeout = false
            this.getAddressPredicitions()
        }, 500)
    }

    getAddressPredicitions() {
        if(!this.address || this.address.length < 4) {
            this.addressPredictions = []
            return;
        }

        this.autocompletionService.getPlacePredictions({
            input: this.address
        }, (places, status) => {
            if(status != google.maps.places.PlacesServiceStatus.OK) {
                this.addressPredictions = []
            } else {
                if(places.length === 1) {
                    this.getLatLng(places[0].description)
                } else {
                    this.addressPredictions = places
                }
            }
        })
    }

    setAddress(address) {
        this.address = address
        this.addressPredictions = []
        this.getLatLng(address)
    }

    getLatLng(address) {
        this.geocoder.geocode({
            address: address
        }, (results, status) => {
            if(status === 'OK') {
                let result = results[0];
                this.updateLatLng(
                    result.geometry.location.lat(),
                    result.geometry.location.lng()
                )
            }
            
        })
    }

    updateLatLng(lat, lng) {
        this.latitude = lat
        this.longitude = lng
        this.placeMapPin(lat, lng)
    }

    loadMap() {
        this.getMapLocation()
        .then((latLng) => {
            let mapOptions = {
                center: latLng,
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
            this.map = new google.maps.Map(this.mapElement.nativeElement, mapOptions)
    
            google.maps.event.addDomListener(this.map, "click", (clickEvent:any) => {
                const lat = clickEvent.latLng.lat()
                const lng = clickEvent.latLng.lng()
                
                this.updateLatLng(lat, lng)

                let location = {
                    lat: lat,
                    lng: lng
                }
                this.geocoder.geocode({
                    location: location
                }, (results, status) => {
                    if(status === 'OK') {
                        this.address = results[0].formatted_address
                    }
                })
            })
        })
    }

    placeMapPin(latitude, longitude) {
        if(!latitude || !longitude) {
            return
        }
        if(!this.map) {
            this.loadMap()
        }
        if(this.mapMarker) {
            this.mapMarker.setMap(null)
        }

        let latLng = new google.maps.LatLng(latitude, longitude)
        this.map.setCenter(latLng)
        this.mapMarker = new google.maps.Marker({
            position: latLng,
            map: this.map
        });
    }

    getMapLocation():Promise<any> {
        if(this.latitude && this.longitude) {
            return Promise.resolve(new google.maps.LatLng(
                this.latitude,
                this.longitude
            ))
        } else {
            return this.geolocation.getCurrentPosition()
            .then((response) => {
                return new google.maps.LatLng(
                    response.coords.latitude,
                    response.coords.longitude
                )
            })
        }
    }
}
