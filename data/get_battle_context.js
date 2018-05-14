
// Hook into the source code of pokemon showdown to simulate team generation
const Battle = require('../../Pokemon-Showdown/sim/battle.js');
var fs = require('fs');  // Node.js library to access files

var BreakException = {};  // Exception used to break out of a ForEach
var GAMES_DATA_PATH = './games_data/';  // Path to game log files
var BATTLE_FORMAT = "gen7randombattle";

filePath = process.argv[2];
seedString = process.argv[3];

provideContext(filePath, seedString);


function provideContext(filePath, seedString) {
    var seedArray = seedString.split(" ").map(function(item) {
        return parseInt(item, 10);
    });

    var simBattle = new Battle({"formatid": BATTLE_FORMAT, "seed": seedArray});
    simBattle.setPlayer("p1", {"name": "p1"});
    simBattle.setPlayer("p2", {"name": "p2"});

    var p1Team = JSON.stringify(simBattle.p1.team, null, 0);
    var p2Team = JSON.stringify(simBattle.p2.team, null, 0);

    // Append JSON of team to file
    fs.appendFile(filePath, "\n" + p1Team + "\n" + p2Team, null);
}

