# Overview
App which handles daily chores via Siri calls through iPhones feature Shortcuts. Made possible by mapping certain Siri Commands to API request targeted the Raspberry Pi 4.

**/Siri/LiloStatus** - Keep track of which dates our dogs needs her medication. Raspberry Pi sense hat displays a color depending on the status. Green - Lilo needs her medication today. Red - Lilo shouln't get medication today. Blue - Lilo already got her medication today.

**/Siri/Senast** - Checks latest date which Lilo got her medication

**/Siri/Matlista** - Generates a fixed number of random dishes with corresponding ingredients sorted by grocery shop layout. The result will be pushed to any users Google Keep account for easier shopping. 

**/Siri/Promenad** - When going out with Lilo, a post request containg "wentout: true" is sent to Pi through Siri. This triggers a timer with marks the time out. The timer keeps ticking unti we send a post request containing "camehome: true" which stops the timer. The number of walks are logged.

**/Siri/AntalPromenader** - Returns the logged number of walks out with Lilo

**/Siri/PromenadSummary** - Returns a summary of walks related info

**/Siri/LiloFick** - Triggers Pi to make a note that Lilo just got her medicine. This changes the sense hats color to blue.

Based on the work made by shrocky2: https://github.com/shrocky2/SiriGarage