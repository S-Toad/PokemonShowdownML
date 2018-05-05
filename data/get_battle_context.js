
const Battle = require('../../Pokemon-Showdown/sim/battle.js');
var fs = require('fs');

var p1 = {"name": "pseduoOne"};
var p2 = {"name": "pseduoTwo"};

fs.readdir('./games_data', function(err, files) {
    if (err) {
        console.error("Error");
        process.exit(1);
    }

    files.forEach(function(file, index) {
        console.log("Providing context for: " + file);
        var filePath = './games_data/' + file;
        fs.readFile(filePath, 'utf8', function(err, data) {
            if (err) {
                console.error("Error");
                process.exit(1);
            }
            
            console.log("Reading: " + filePath);
            data.split("\n").forEach(function(line, lineIndex) {
                if (line.includes("|seed|")) {

                    console.log(line);
                    var seedArray = line.replace("|seed|", "").replace("\r", "").split(",").map(function(item) {
                        return parseInt(item, 10);
                    });
                    console.log(seedArray);

                    var options = {
                        "formatid": "gen7randombattle",
                        "seed": seedArray
                    };

                    console.log(options)

                    var pseduoBattle = new Battle(options);
                    
                    pseduoBattle.setPlayer("p1", p1);
                    pseduoBattle.setPlayer("p2", p2);
                    
                    var p1Team = JSON.stringify(pseduoBattle.p1.team, null, 0);
                    var p2Team = JSON.stringify(pseduoBattle.p2.team, null, 0);

                    fs.appendFile(filePath, "\n" + p1Team + "\n" + p2Team, null);
                }
            });
        });
    });
});
