using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using System.Xml;
using System.Xml.Serialization;
using Microsoft.Xna.Framework.Graphics;

namespace Core.Pipeline
{
    public class XmlVector3
    {
        [XmlAttribute]
        public Single X = 0;

        [XmlAttribute]
        public Single Y = 0;

        [XmlAttribute]
        public Single Z = 0;

        [XmlIgnore]
        public static XmlVector3 Zero = new XmlVector3(0, 0, 0);

        [XmlIgnore]
        public static XmlVector3 One = new XmlVector3(1, 1, 1);

        public XmlVector3() { }

        public XmlVector3(Single x, Single y, Single z)
        {
            X = x; Y = y; Z = z;
        }

        public XmlVector3(Vector3 vector)
        {
            X = vector.X;
            Y = vector.Y;
            Z = vector.Z;
        }

        public void SetZero()
        {
            X = Y = Z = 0;
        }

        public Boolean IsZero()
        {
            return X == 0 && Y == 0 && Z == 0;
        }

        public void SetOne()
        {
            X = Y = Z = 1;
        }

        public Boolean IsOne()
        {
            return X == 1 && Y == 1 && Z == 1;
        }

        public static Vector3 operator +(Vector3 vector3, XmlVector3 xmlVector3)
        {
            return new Vector3(vector3.X + xmlVector3.X, vector3.Y + xmlVector3.Y, vector3.Z + xmlVector3.Z);
        }

        public Vector3 ToVector3()
        {
            return new Vector3(X, Y, Z);
        }

        public Color ToColor()
        {
            return new Color(ToVector3());
        }

        public Matrix ToTranslationMatrix()
        {
            return Matrix.CreateTranslation(X, Y, Z);
        }

        public Matrix ToRotationMatrix()
        {
            return Matrix.CreateRotationX(MathHelper.ToRadians(X)) *
                Matrix.CreateRotationY(MathHelper.ToRadians(Y)) *
                Matrix.CreateRotationZ(MathHelper.ToRadians(Z));
        }

        public Matrix ToScaleMatrix()
        {
            return Matrix.CreateScale(X, Y, Z);
        }

        public override string ToString()
        {
            return ToVector3().ToString();
        }
    }
}
