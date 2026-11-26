# KEY-Mint: lokaler Test vom 26.11.2026

Der direkte KEY-Mint ist im Vertragsentwurf implementiert und mit Test-KEY erfolgreich geprüft. Alle 33 Foundry-Vertragstests sind bestanden, darunter 19 Tests für den bezahlten Mint. Es gab keine Transaktion auf einer öffentlichen Blockchain und keinen Einsatz echter KEY.

## Geld und NFT

- Der gesamte konfigurierte KEY-Preis geht direkt vom Käufer an `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1`.
- Das NFT geht an die vom Käufer bestätigte Empfängeradresse. Diese kann sich von seiner zahlenden Wallet unterscheiden.
- Der Collection-Vertrag und die Deployment-Wallet behalten keine Mint-Einnahmen.
- Die 10 % Royalty bei späteren Verkäufen werden nicht vom Erst-Mint abgezogen.
- Ein bestätigter Preis von 500.000 Test-KEY zahlt 500.000 Test-KEY aus; ein separat konfigurierter Preis von 375.000 zahlt 375.000 aus. Das ist kein Nachweis einer bereits angebundenen Staking-Rabattprüfung.

## Erfolgreich geprüfte Fälle

1. Mint ist nach Deployment deaktiviert; nur der Vertragsinhaber kann Angebote freigeben, zurückziehen oder den Mint aktivieren/pausieren.
2. Vollständiger Zahlungseingang beim Creator, exakter Käuferabzug, korrekter NFT-Eigentümer und korrekte Metadaten.
3. Ein geänderter Preis oder eine geänderte Metadaten-URI macht die vorher angezeigte Bestätigung ungültig und löst keine Zahlung aus.
4. Fehlendes Guthaben oder fehlende KEY-Allowance erzeugt kein NFT und keine Creator-Zahlung.
5. Lehnt der NFT-Empfänger die Zustellung ab, werden Zahlung, Allowance-Verbrauch und Inventaränderung zurückgesetzt.
6. Fehlgeschlagene Token-Transfers, zu geringe Auszahlung oder unerwartete zusätzliche Käuferabbuchung brechen den gesamten Mint ab.
7. Ein zweiter Mint derselben Edition, nicht freigegebene Editionen und zurückgezogene Angebote lösen keine zweite Zahlung aus.
8. Ein Callback des NFT-Empfängers kann keinen verschachtelten Mint ausführen.
9. Eine spätere Übertragung der Collection-Verwaltung leitet die Mint-Einnahmen nicht an eine andere Wallet um.

## Stand vor einem öffentlichen Mint

Die App bleibt für Zahlungen gesperrt. Es gibt keine veröffentlichte Collection-Adresse und kein freigegebenes Produktionsinventar. Die Zahlen-IDs im Test sind reine Testwerte und keine endgültige Zuordnung der Inseln zu Onchain-Token-IDs.

Vor dem Start müssen der echte KEY-Vertrag und seine Dezimalstellen geprüft, die Wallet-Bedienung angeschlossen, Editionen und Metadaten verbindlich zugeordnet sowie regionale/zufällige Auswahl und nachweisbare Staking-Rabatte ergänzt werden. Anschließend sind Zahlungseingang, NFT-Zuordnung und OpenSea-Anzeige mit einer echten autorisierten Onchain-Transaktion zu prüfen. Creator-Fee-Einstellungen und deren Durchsetzung auf OpenSea bleiben ebenfalls offen.

## Reproduzierbarkeit

Vertrag: `contracts/Islands.sol`; Zahlungstests: `test/IslandsMint.t.sol`; Testwährungen/Empfänger: `test/KeyMintMocks.sol`. Solidity 0.8.24, OpenZeppelin Contracts 5.2.0, forge-std 1.9.6. `forge test -vvv` führt die Vertragstests aus. Im lokalen Test ersetzen Mocks den KEY-Vertrag; diese Manipulation existiert ausschließlich in der Testumgebung.
