# Geometriska grundregler – version 1

Steg 8 inför ett konservativt geometrilager. Det är avsiktligt mindre ambitiöst än en fysik- eller fullständig LEGO-connection-motor.

## Regler som kontrolleras

För enkla rektangulära LDraw-delar vars beskrivning matchar `Brick W x D` eller `Plate W x D`:

- X/Z-position ska ligga på 10 LDU half-stud-grid.
- Y-position ska ligga på 8 LDU plate-height-grid.
- rotationen ska vara en signerad permutationsmatris, dvs. endast 90-graders axelrotationer.
- normala studs-up-delar får inte ha positivt överlappande axis-aligned bounding boxes.
- beröring vid en gemensam yta räknas inte som kollision.

Standardmått i detta lager är 20 LDU per stud, 8 LDU per plate och 24 LDU per brick.

## Medvetna begränsningar

- Delprofiler härleds bara för enkla `Brick` och `Plate` med rektangulär footprint.
- Rotationsvalidering görs för alla profilerade delar, men kollisionsenvelopes beräknas i v1 bara för oroterade studs-up-profiler.
- Unsupported parts ger varning och geometrikontrollen blir `partial`, inte ett falskt påstående om full verifiering.
- Ingen kontroll av studs/anti-studs, clips, pins, axlar, gångjärn, SNOT-connections, clutch, tyngdpunkt eller hållfasthet görs ännu.
- En godkänd geometrirapport betyder därför "inga fel som v1-reglerna kan upptäcka", inte "fysiskt bevisat byggbar".
