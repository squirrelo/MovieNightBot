Utility = {};

Utility.CharIsNumber = function(char) {
	return char == '0' || char == '1' || char == '2' || char == '3' || char == '4' || char == '5' || char == '6' || char == '7' || char == '8' || char == '9';
}


Utility.GetQueryValue = function(key) {
	var value = "";
	var queryString = window.location.search;
	if (queryString) {
		params = new URLSearchParams(queryString);
		if (params) {
			value = params.get(key);
		}
	}

	return value;
}

Mathf = {};

Mathf.Lerp = function(value1, value2, a) {
	return value1 + (value2 - value1) * a;
}

Mathf.LerpClamped = function(value1, value2, a) {
	a = a < 0 ? 0 : a;
	a = a > 1 ? 1 : a;
	return value1 + (value2 - value1) * a;
}


function Vector3(x, y, z) {
	this.x = x;
	this.y = y;
	this.z = z;

	this.Set = function(x, y, z) {
		this.x = x;
		this.y = y;
		this.z = z;
	}

	this.Add = function(other) {
		this.x += other.x;
		this.y += other.y;
		this.z += other.z;
	}

	this.Lerp = function(vector1, vector2, a) {
		let newVector = new Vector3();
		newVector.x = Math2.Lerp(vector1.x, vector2.x, a);
		newVector.y = Math2.Lerp(vector1.y, vector2.y, a);
		newVector.z = Math2.Lerp(vector1.z, vector2.z, a);
		return newVector;
	}

	this.Scale = function(scalar) {
		this.x *= scalar;
		this.y *= scalar;
		this.z *= scalar;
	}

	this.RGB = function() {
		return "rgb(" + this.x + "," + this.y + "," + this.z + ")";
	}

	this.ToString = function() {
		return "(" + this.x + "," + this.y + "," + this.z + ")";
	}
}