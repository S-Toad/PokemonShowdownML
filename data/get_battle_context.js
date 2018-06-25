
// Hook into the source code of pokemon showdown to simulate team generation
const Battle = require('./Pokemon-Showdown/sim/battle.js');
const Pokedex = require('./Pokemon-Showdown/data/pokedex.js');
const Movesdex = require('./Pokemon-Showdown/data/moves.js');
const Itemdex = require('./Pokemon-Showdown/data/items.js')
const Abilitiesdex = require('./Pokemon-Showdown/data/abilities.js')

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

    fs.appendFile(filePath, genTeamStrRep(simBattle.p1.team), null);
    fs.appendFile(filePath, genTeamStrRep(simBattle.p2.team), null);
}

function genTeamStrRep(jsonTeam) {
    var teamStr = "";
    for (i = 0; i < 6; i++) {
        teamStr += genPokeStrRep(jsonTeam[i]);
        if (i != 5) {
            teamStr += ":";
        }
    }
    return teamStr + '\n';
}

function genPokeStrRep(pokeJSON) {
    var pokeStr = "";
    name = pokeJSON['name'].toLowerCase();
    moves = pokeJSON['moves'];
    ability = pokeJSON['ability'].replace(" ", "").toLowerCase();
    item = pokeJSON['item'].replace(" ", "").toLowerCase();
    pokedexEntry = Pokedex.BattlePokedex[name];

    pokeStr = pokedexEntry.num + ','
        + Itemdex.BattleItems[item].num + ','
        + Abilitiesdex.BattleAbilities[ability].num + ','
        + getTypeValue(pokedexEntry.types[0]) + ','
        + getTypeValue(pokedexEntry.types[1]) + ',';

    for (j = 0; j < 4; j++) {
        pokeStr += Movesdex.BattleMovedex[moves[j].toLowerCase()].num;
        if (j != 3) {
            pokeStr += "|";
        }
    }

    return pokeStr;
}

function getTypeValue(typeString) {
    if (typeString == void 0) {
        return -1;
    }
    typeString = typeString.toLowerCase();
    return [
        'normal','fighting','flying',
        'poison','ground','rock',
        'bug','ghost','steel',
        'fire','water','grass',
        'electric','psychic','ice',
        'dragon','dark','fairy'
    ].indexOf(typeString);
}
